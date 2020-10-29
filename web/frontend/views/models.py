from backend.models import *
from django.views.generic import TemplateView

class ModelView(TemplateView):
    # list all persons and render them into the frontend

    def create_context(self, request):
        person_list = Person.objects.all()
        # get current person id from url
        pk = request.get_full_path().split("/")[-1]
        model = Model.objects.get(pk=int(pk))
        activity_list = Activity.objects.all()
        person_list = Person.objects.all()
        model_list = Model.objects.all()
        try:
            benchmark = model.benchmark
        except:
            benchmark = None

        if benchmark is not None:
            conf_mat_html = self.get_conf_mat(model)
            metrics_html = self.get_metrics(model)
            class_accs_html = self.get_df_class_acts(model)
        else:
            conf_mat_html = None
            metrics_html = None
            class_accs_html = None

        context = {
            'model': model,
            'benchmark':benchmark,
            'person_list': person_list,
            'activity_list': activity_list,
            'conf_mat_html': conf_mat_html,
            'metrics_html' : metrics_html,
            'class_accs_html': class_accs_html
        }
        return context

    def get_conf_mat(self, model):
        import pandas as pd
        with model.benchmark.df_conf_mat.open(mode='r') as f:
            df = pd.read_csv(f)
            cols = df.columns
            new_cols = ['ConfMat']
            for col in cols[1:]:
                words = col.split('_')
                letters = ''
                for word in words:
                    letters = letters + word[0]
                new_cols.append(letters)

            df.columns = new_cols

            df.set_index('ConfMat', inplace=True)
            html = df.to_html(classes=["table-bordered", "table-striped", "table-hover"])
            return html

    def get_df_class_acts(self, model):
        import pandas as pd
        with model.benchmark.df_class_acts.open(mode='r') as f:
            df = pd.read_csv(f, delimiter=',')
            unamed0 = 'Unnamed: 0'
            model_col_name = 'Model'
            class_acc_name = 'class acc'
            df.set_index(unamed0)
            df.rename(columns={unamed0:model_col_name}, inplace=True)
            df[model_col_name].iloc[0] = model.datainstance.name
            num_classes = len(df.columns)-1
            df[class_acc_name] = df.iloc[0].drop(model_col_name).sum()/num_classes

            df.set_index(model_col_name, inplace=True)
            df = df.transpose()
            html = df.to_html(classes=["table-bordered", "table-striped", "table-hover"])
            return html



    def get_metrics(self, model):
        import pandas as pd
        with model.benchmark.df_metrics.open(mode='r') as f:
            df = pd.read_csv(f, delimiter='\t')
            df.columns = ['Metrics']
            html = df.to_html(classes=["table-bordered", "table-striped", "table-hover"])
            return html

    def is_correct_model_selected(self, request):
        try:
            pk = request.get_full_path().split("/")[-1]
            model = Model.objects.get(pk=int(pk))
            return True
        except:
            return False

    def get(self, request):
        if self.is_correct_model_selected(request):
            context = self.create_context(request)
            return render(request, 'models.html', context)
        raise ValueError

    def post(self, request):
        intent = request.POST.get("intent","")
        #create object not through serialzier
        if (intent == "uncouple"):
            pk = request.POST.get("pk", "")
            request.path=request.path + "%s"%(pk)

        context = self.create_context(request)
        return render(request, 'models.html', context)

