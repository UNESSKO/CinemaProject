from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, Movie, Session, Hall, Director, Review, Booking


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        help_text='Введите действующий email адрес'
    )
    birth_date = forms.DateField(
        required=False,
        label='Дата рождения',
        help_text='Формат: ГГГГ-ММ-ДД (например, 1990-01-01)',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'birth_date', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Переводим все подсказки и метки на русский
        self.fields['username'].label = 'Логин'
        self.fields[
            'username'].help_text = 'Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.'
        self.fields['username'].widget.attrs.update({'placeholder': 'Введите логин'})

        self.fields['email'].widget.attrs.update({'placeholder': 'your@email.com'})

        self.fields['birth_date'].widget.attrs.update({'placeholder': 'ГГГГ-ММ-ДД'})

        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].help_text = '''
            <ul>
                <li>Пароль не должен быть слишком похож на другую вашу личную информацию.</li>
                <li>Пароль должен содержать не менее 8 символов.</li>
                <li>Пароль не может быть слишком простым и распространённым.</li>
                <li>Пароль не может состоять только из цифр.</li>
            </ul>
        '''
        self.fields['password1'].widget.attrs.update({'placeholder': 'Введите пароль'})

        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['password2'].help_text = 'Для подтверждения введите тот же пароль ещё раз.'
        self.fields['password2'].widget.attrs.update({'placeholder': 'Повторите пароль'})


class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ['name', 'birth_date', 'birth_place', 'biography', 'photo']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'biography': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'name': 'Имя режиссёра',
            'birth_date': 'Дата рождения',
            'birth_place': 'Место рождения',
            'biography': 'Биография',
            'photo': 'Фото',
        }


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'duration_min', 'rating', 'release_year', 'poster', 'director', 'genres']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'genres': forms.SelectMultiple(attrs={'size': 5}),
        }
        labels = {
            'title': 'Название фильма',
            'description': 'Описание',
            'duration_min': 'Длительность (минуты)',
            'rating': 'Рейтинг',
            'release_year': 'Год выпуска',
            'poster': 'Постер',
            'director': 'Режиссёр',
            'genres': 'Жанры',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'poster' in self.fields:
            self.fields['poster'].widget.attrs.update({'accept': 'image/*'})


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['movie', 'hall', 'start_time', 'price']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'movie': 'Фильм',
            'hall': 'Зал',
            'start_time': 'Время начала',
            'price': 'Цена (руб)',
        }


class HallForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = ['number', 'capacity', 'sound_system']
        labels = {
            'number': 'Номер зала',
            'capacity': 'Вместимость',
            'sound_system': 'Звуковая система',
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Поделитесь впечатлениями о фильме...'}),
        }
        labels = {
            'rating': 'Оценка (1-5)',
            'comment': 'Комментарий',
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seat_row', 'seat_number']
        labels = {
            'seat_row': 'Ряд',
            'seat_number': 'Место',
        }
        help_texts = {
            'seat_row': 'Выберите ряд от 1 до 10',
            'seat_number': 'Выберите место от 1 до 20',
        }

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        seat_row = cleaned_data.get('seat_row')
        seat_number = cleaned_data.get('seat_number')

        if self.session and seat_row and seat_number:
            from .models import Booking
            if Booking.objects.filter(session=self.session, seat_row=seat_row, seat_number=seat_number,
                                      status='confirmed').exists():
                raise forms.ValidationError('Это место уже забронировано или куплено!')

            if seat_row < 1 or seat_row > 10:
                raise forms.ValidationError('Неверный номер ряда (1-10)')
            if seat_number < 1 or seat_number > 20:
                raise forms.ValidationError('Неверный номер места (1-20)')

        return cleaned_data