from django.db import models
from accounts.models import User
# Create your models here.

class EmployeeForm(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE, 
                                   related_name='employee_forms', 
                                   null=True)    
    dynamic_fields = models.JSONField(null=True) 
    
    def __str__(self):
        return f"Form for {self.created_by.username} "


class EmployeeManagement(models.Model):
    form = models.ForeignKey(EmployeeForm, on_delete=models.CASCADE, related_name='employee_profile')
    dynamic_data = models.JSONField(default=dict, null=True)

    def __str__(self):
        return f"Employee Profile for {self.form.created_by.username}"