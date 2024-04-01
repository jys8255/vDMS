from django.contrib import admin
from registerapp.models import DtcCode,ErrCompId,Scenario


@admin.register(Scenario)
class LoggingAdmin(admin.ModelAdmin):
    list_display = ('id','file_name','eADP','project_code',
                    'test_Scenario_ID','sw_version','weather',
                    'location','get_dtc_codes','get_err_comp',)

    def get_dtc_codes(self, obj):
        return ", ".join([dtc.name for dtc in obj.dtc_code.all()])

    get_dtc_codes.short_description = "DTC Codes"

    def get_err_comp(self, obj):
        return ", ".join([err.name for err in obj.err_comp_id.all()])

    get_err_comp.short_description = "ERR Comp"


@admin.register(DtcCode)
class DtcCodeAdmin(admin.ModelAdmin):  # 클래스 이름 올바르게 지정
    list_display = ('id', 'name')

@admin.register(ErrCompId)
class ErrCompIdAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')