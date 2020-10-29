from backend.models import *
from django.views.generic import TemplateView

class ModelSelectionView(TemplateView):
    def create_context(self, request):
        person_list = Person.objects.all()
        model_list = Model.objects.all()
        context = {
            'person_list': person_list,
            'model_list': model_list,
        }
        return context

    def get(self, request):
        context = self.create_context(request)
        return render(request, 'model_selection.html', context)

    def delete_model(self, request):
        pk = request.POST.get("pk", "")
        print('pk: ', pk)
        model = Model.objects.filter(id=pk)[0]
        model.delete()

    def post(self, request):
        intent = request.POST.get("intent","")
        #create object not through serialzier
        if (intent == "delete"):
            self.delete_model(request)


        context = self.create_context(request)
        return render(request, 'model_selection.html', context)

