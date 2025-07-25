from __future__ import annotations

import os
from flask import Blueprint, redirect
from flask_appbuilder import BaseView, expose

from airflow.auth.managers.models.resource_details import AccessView
from airflow.plugins_manager import AirflowPlugin
from airflow.www.auth import has_access_view


# Ruta absoluta hacia tus reportes (ajusta si usas Docker!)
reports_path = os.path.abspath("dags/modules/gxe_validation_reports/reports")

# Blueprint: este nombre DEBE SER ÚNICO en Airflow
gxe_bp = Blueprint(
    "gxe_reports_static",
    __name__,
    static_folder=reports_path,
    static_url_path="/gxe_reports_static",  # <- Ruta que será servida en el navegador
)


class GXEReportsView(BaseView):
    default_view = "index"

    @expose("/")
    @has_access_view(AccessView.PLUGINS)
    def index(self):
        return redirect("/gxe_reports_static")  # Redirige al folder servido


class GXEReportsPlugin(AirflowPlugin):
    name = "GXEReports"
    flask_blueprints = [gxe_bp]
    appbuilder_views = []
