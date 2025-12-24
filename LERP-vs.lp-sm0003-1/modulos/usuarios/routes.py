from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm
from .models import Usuario

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ========================
# LOGIN
# ========================
@admin_bp.route("/login", methods=["GET", "POST"])
def login_admin():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))
        flash("Usuário ou senha incorretos.", "danger")

    return render_template("admin/login.html", form=form)


# ========================
# LOGOUT
# ========================
@admin_bp.route("/logout")
@login_required
def logout_admin():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("admin.login_admin"))


# ========================
# DASHBOARD
# ========================
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin/dashboard.html", user=current_user)
