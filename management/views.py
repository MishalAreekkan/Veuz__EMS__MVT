from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import EmployeeForm, EmployeeManagement
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

@login_required
def create_form(request):   
    if request.method == 'POST':
        fields = json.loads(request.body.decode('utf-8')).get('fields', [])
        form= EmployeeForm.objects.get(created_by=request.user)
        form.dynamic_fields = fields
        form.save() 
        return redirect('form_create')
    employee_form,_ = EmployeeForm.objects.get_or_create(created_by=request.user)
    return render(request, 'management/form_create.html',{"data":employee_form})


@csrf_exempt
def update_field_order(request):
    if request.method == 'POST':
        try:
            field_data = json.loads(request.POST.get('field_data', '[]'))
            for field in field_data:
                field.pop("id")
                field.pop("order")
            EmployeeForm.objects.filter(created_by=request.user).update(dynamic_fields=field_data)
            return redirect('form_create')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def create_employee(request):
    try:
        form = EmployeeForm.objects.get(created_by=request.user)
    except EmployeeForm.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'EmployeeForm not found.'}, status=404)
    
    dynamic_fields = form.dynamic_fields 
    if not isinstance(dynamic_fields, list) or not all(isinstance(field, dict) for field in dynamic_fields):
        return JsonResponse({'success': False, 'error': 'Invalid dynamic_fields format.'}, status=400)
    
    dynamic_data = {}
    employee_data = EmployeeManagement.objects.filter(form=form).last()
    if employee_data and employee_data.dynamic_data:
        dynamic_data = json.loads(employee_data.dynamic_data)

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8')).get('data', {})
        errors = []
        for field in dynamic_fields:
            label = field.get('label')
            required = field.get('required', False)
            value = data.get(label)

            if required and not value:
                errors.append(f"The field '{label}' is required.")

        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        EmployeeManagement.objects.create(form=form, dynamic_data=json.dumps(data)) 
        return JsonResponse({'success': True, 'message': 'Employee created successfully!'})
    return render(request, 'management/create_employee.html', {
        'form': form,
        'dynamic_fields': dynamic_fields,
        'dynamic_data': dynamic_data
    })


@login_required
def employee_list(request):
    employees = EmployeeManagement.objects.filter(form__created_by=request.user).values() 
    employee_data = []
    dynamic_headers = []

    if employees:
        dynamic_data = json.loads(employees[0].get('dynamic_data', '{}'))
        dynamic_data.pop('csrfmiddlewaretoken')
        dynamic_headers = list(dynamic_data.keys())
        print(dynamic_data,'dedddddd')

    search_field = request.GET.get('searchField', '')
    search_value = request.GET.get('searchValue', '')

    if search_field and search_value:
        filtered_employees = []
        for employee in employees:
            dynamic_data = json.loads(employee.get('dynamic_data', '{}'))
            if search_field in dynamic_data and search_value.lower() in dynamic_data[search_field].lower():
                filtered_employees.append(employee)
        employees = filtered_employees
    for employee in employees:
        dynamic_data = json.loads(employee.get('dynamic_data', '{}'))
        formatted_data = {}

        for key, value in dynamic_data.items():
            formatted_data[key] = value
            formatted_data["id"] = employee['id']
        employee_data.append(formatted_data)
    return render(request, 'management/employees.html', {
        'employees': employee_data,
        'headers': dynamic_headers,
        'searchField': search_field,
        'searchValue': search_value
    })


@login_required
def edit_employee(request, employee_id):
    try:
        form = EmployeeForm.objects.get(created_by=request.user)
        employee = EmployeeManagement.objects.get(id=employee_id)
    except EmployeeManagement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found.'}, status=404)

    try:
        dynamic_data = json.loads(employee.dynamic_data) if employee.dynamic_data else {}
    except json.JSONDecodeError:
        dynamic_data = {}

    if request.method == 'POST':
        data = request.POST
        for key, value in data.items():
            if key in dynamic_data:
                dynamic_data[key] = value
        
        employee.dynamic_data = json.dumps(dynamic_data)
        employee.save()
        return redirect('employee_list')
    return render(request, 'management/edit_employee.html', {
        'form': form, 
        'employee': employee, 
        'dynamic_data': dynamic_data
    })
    
    
@login_required    
def delete_employee(request, id):
    if request.method == 'POST':
        try:
            employee = EmployeeManagement.objects.get(id=id)
            employee.delete()
            return redirect("employee_list")
        except EmployeeManagement.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Employee not found.'}, status=404)
    return redirect("employee_list")
