from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	             path('UserLogin.html', views.UserLogin, name="UserLogin"), 
	             path('Register.html', views.Register, name="Register"),
		     path('RegisterAction', views.RegisterAction, name="RegisterAction"),	
	             path('UserLoginAction', views.UserLoginAction, name="UserLoginAction"),	
		     path('ComposeMail.html', views.ComposeMail, name="ComposeMail"),
		     path('ComposeMailAction', views.ComposeMailAction, name="ComposeMailAction"),
		     path('ViewEmail', views.ViewEmail, name="ViewEmail"),	
		     path('DownloadAction', views.DownloadAction, name="DownloadAction"),	
		     path('DecryptMessage', views.DecryptMessage, name="DecryptMessage"),	
]
