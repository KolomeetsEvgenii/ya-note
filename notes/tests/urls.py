from django.urls import reverse, reverse_lazy

HOME_URL = reverse_lazy('notes:home')
ADD_URL = reverse_lazy('notes:add')
LIST_URL = reverse_lazy('notes:list')
SUCCESS_URL = reverse_lazy('notes:success')

LOGIN_URL = reverse_lazy('users:login')
SIGNUP_URL = reverse_lazy('users:signup')
LOGOUT_URL = reverse_lazy('users:logout')


def note_url(name: str, slug: str) -> str:
    return reverse(name, args=(slug,))
