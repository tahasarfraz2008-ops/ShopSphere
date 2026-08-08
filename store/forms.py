from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(
        attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'you@example.com'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'placeholder': '+1 555 000 0000'}))
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Street address'}))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'placeholder': 'City'}))
    country = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Country'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone',
                  'address', 'city', 'country', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        user.address = self.cleaned_data.get('address', '')
        user.city = self.cleaned_data.get('city', '')
        user.country = self.cleaned_data.get('country', '')
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your thoughts about this product...'}),
        }
