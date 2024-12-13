from django.urls import path
from . import views

urlpatterns = [
    path('form_create/', views.create_form, name='form_create'),
    path('employee_create/', views.create_employee, name='employee_create'),
    path('list/', views.employee_list, name='employee_list'),
    path('employee_edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('delete_emp/<int:id>/', views.delete_employee, name='delete_emp'),
    path('update_field_order/', views.update_field_order, name='update_field_order'),
]