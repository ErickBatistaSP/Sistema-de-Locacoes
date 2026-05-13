from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.forms import inlineformset_factory
from django import forms

from combo.models import ComboLocacao

from cliente.models import Cliente
from item.models import Item
from locacao.models import Locacao
from itemlocacao.models import ItemLocacao

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# ─── LOGIN ───────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'auth/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ─── FORMS ───────────────────────────────────────────────────────────────────

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'bairro', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(27) 99999-9999'}),
            'bairro': forms.TextInput(attrs={'placeholder': 'Nome do bairro'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, número'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome', '').strip()
        telefone = cleaned_data.get('telefone', '').strip()

        # Nome: remove espaços extras e capitaliza
        nome = ' '.join(nome.split()).title()
        cleaned_data['nome'] = nome

        # Telefone: valida o formato
        import re
        if not re.match(r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$', telefone):
            self.add_error('telefone', 'Formato inválido. Use: (27) 99999-9999 ou 27999999999')

        # Validação de duplicata
        qs = Cliente.objects.filter(nome__iexact=nome, telefone=telefone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe um cliente com esse nome e telefone.')

        return cleaned_data


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['tipo', 'quantidade_estoque']
        widgets = {
            'quantidade_estoque': forms.NumberInput(attrs={'min': 0}),
        }


class LocacaoForm(forms.ModelForm):
    class Meta:
        model = Locacao
        fields = ['cliente', 'data_inicio', 'data_fim', 'preco_total', 'observacoes',
                  'endereco_rua', 'endereco_numero', 'endereco_bairro', 'endereco_referencia']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'preco_total': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'placeholder': 'R$ 0,00', 'value': ''}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observações opcionais...'}),
            'endereco_rua': forms.TextInput(attrs={'placeholder': 'Rua, Avenida...'}),
            'endereco_numero': forms.TextInput(attrs={'placeholder': 'Número'}),
            'endereco_bairro': forms.TextInput(attrs={'placeholder': 'Bairro'}),
            'endereco_referencia': forms.TextInput(attrs={'placeholder': 'Ponto de referência'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim:
            if data_fim < data_inicio:
                raise forms.ValidationError('A data de fim não pode ser anterior à data de início.')

        return cleaned_data

class ItemLocacaoForm(forms.ModelForm):
    class Meta:
        model = ItemLocacao
        fields = ['item', 'quantidade']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Qtd'}),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if not quantidade or quantidade <= 0:
            raise forms.ValidationError('Informe uma quantidade maior que zero.')
        return quantidade

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantidade = cleaned_data.get('quantidade')

        if item and quantidade:
            if self.instance.pk:
                anterior = ItemLocacao.objects.get(pk=self.instance.pk)
                disponivel = item.quantidade_estoque + anterior.quantidade
            else:
                disponivel = item.quantidade_estoque

            if quantidade > disponivel:
                raise forms.ValidationError(
                    f"Estoque insuficiente! Disponível: {disponivel} unidade(s) de {item.get_tipo_display()}."
                )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.preco_unitario is None:
            instance.preco_unitario = 0
        if commit:
            instance.save()
        return instance


ItemLocacaoFormSet = inlineformset_factory(
    Locacao, ItemLocacao,
    form=ItemLocacaoForm,
    extra=1,
    can_delete=False,
    min_num=0,
    validate_min=True,
)

class ComboLocacaoForm(forms.ModelForm):
    class Meta:
        model = ComboLocacao
        fields = ['combo', 'quantidade']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Qtd'}),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if not quantidade or quantidade <= 0:
            raise forms.ValidationError('Informe uma quantidade maior que zero.')
        return quantidade


ComboLocacaoFormSet = inlineformset_factory(
    Locacao, ComboLocacao,
    form=ComboLocacaoForm,
    extra=1,
    can_delete=False,
    min_num=0,
    validate_min=False,
)

# ─── DASHBOARD ───────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    itens = Item.objects.all()
    # Pega a quantidade máxima para a barra de progresso
    max_estoque = max((i.quantidade_estoque for i in itens), default=1)
    for item in itens:
        item.quantidade_max = max_estoque

    faturamento = sum(
    l.preco_total for l in Locacao.objects.filter(status='finalizada')
    if l.preco_total is not None
    )

    return render(request, 'dashboard/dashboard.html', {
        'total_locacoes': Locacao.objects.filter(status='ativa').count(),
        'total_clientes': Cliente.objects.count(),
        'total_itens': Item.objects.count(),
        'faturamento': faturamento,
        'locacoes_recentes': Locacao.objects.select_related('cliente').order_by('-data_inicio')[:5],
        'itens': itens,
    })


# ─── CLIENTES ────────────────────────────────────────────────────────────────
@login_required
def clientes_list(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(nome__icontains=q)
    return render(request, 'clientes/lista.html', {'clientes': clientes})

@login_required
def cliente_criar(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente cadastrado com sucesso!')
        return redirect('clientes_list')
    return render(request, 'clientes/form.html', {'form': form})

@login_required
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente atualizado!')
        return redirect('clientes_list')
    return render(request, 'clientes/form.html', {'form': form})

@login_required
def cliente_deletar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente removido.')
        return redirect('clientes_list')
    return render(request, 'clientes/deletar.html', {'cliente': cliente})


# ─── ITENS ───────────────────────────────────────────────────────────────────
@login_required
def itens_list(request):
    itens = Item.objects.all()
    return render(request, 'itens/lista.html', {'itens': itens})

@login_required
def item_criar(request):
    form = ItemForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Item cadastrado!')
        return redirect('itens_list')
    return render(request, 'itens/form.html', {'form': form})

@login_required
def item_editar(request, pk):
    item = get_object_or_404(Item, pk=pk)
    form = ItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, 'Item atualizado!')
        return redirect('itens_list')
    return render(request, 'itens/form.html', {'form': form})

@login_required
def item_deletar(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item removido.')
        return redirect('itens_list')
    return render(request, 'itens/deletar.html', {'item': item})


# ─── LOCAÇÕES ────────────────────────────────────────────────────────────────
@login_required
def locacoes_list(request):
    locacoes = Locacao.objects.select_related('cliente').order_by('-data_inicio')
    status = request.GET.get('status')
    if status:
        locacoes = locacoes.filter(status=status)
    return render(request, 'locacoes/lista.html', {'locacoes': locacoes})

@login_required
def locacao_detalhe(request, pk):
    locacao = get_object_or_404(Locacao, pk=pk)
    itens = locacao.items.select_related('item').all()
    combos = locacao.combos.select_related('combo').all()
    return render(request, 'locacoes/detalhe.html', {'locacao': locacao, 'itens': itens, 'combos': combos})

@login_required
def locacao_criar(request):
    form = LocacaoForm(request.POST or None)
    formset = ItemLocacaoFormSet(request.POST or None, prefix='items')
    combo_formset = ComboLocacaoFormSet(request.POST or None, prefix='combos')

    if form.is_valid() and formset.is_valid() and combo_formset.is_valid():
        # Verifica se tem pelo menos 1 item ou 1 combo
        tem_item = any(f.cleaned_data.get('item') for f in formset if f.cleaned_data)
        tem_combo = any(f.cleaned_data.get('combo') for f in combo_formset if f.cleaned_data)

        if not tem_item and not tem_combo:
            messages.error(request, 'Adicione pelo menos um item ou um combo na locação.')
        else:
            locacao = form.save()
            formset.instance = locacao
            formset.save()
            combo_formset.instance = locacao
            combo_formset.save()
            messages.success(request, 'Locação criada com sucesso!')
            return redirect('locacao_detalhe', pk=locacao.pk)

    return render(request, 'locacoes/form.html', {'form': form, 'formset': formset, 'combo_formset': combo_formset})

@login_required
def locacao_editar(request, pk):
    locacao = get_object_or_404(Locacao, pk=pk)
    form = LocacaoForm(request.POST or None, instance=locacao)
    formset = ItemLocacaoFormSet(request.POST or None, instance=locacao, prefix='items')
    combo_formset = ComboLocacaoFormSet(request.POST or None, instance=locacao, prefix='combos')

    if form.is_valid() and formset.is_valid() and combo_formset.is_valid():
        # Verifica se tem pelo menos 1 item ou 1 combo
        tem_item = any(f.cleaned_data.get('item') for f in formset if f.cleaned_data)
        tem_combo = any(f.cleaned_data.get('combo') for f in combo_formset if f.cleaned_data)

        if not tem_item and not tem_combo:
            messages.error(request, 'Adicione pelo menos um item ou um combo na locação.')
        else:
            locacao = form.save()
            formset.instance = locacao
            formset.save()
            combo_formset.instance = locacao
            combo_formset.save()
            messages.success(request, 'Locação criada com sucesso!')
            return redirect('locacao_detalhe', pk=locacao.pk)

    return render(request, 'locacoes/form.html', {'form': form, 'formset': formset, 'combo_formset': combo_formset})

@login_required
def locacao_finalizar(request, pk):
    locacao = get_object_or_404(Locacao, pk=pk)
    if request.method == 'POST':
        locacao.finalizar()
        messages.success(request, f'Locação de {locacao.cliente.nome} finalizada. Estoque devolvido!')
        return redirect('locacoes_list')
    return render(request, 'locacoes/finalizar.html', {'locacao': locacao})
