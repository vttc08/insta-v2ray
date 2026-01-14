import logging
from configuration import api_password, subscription_password, tunnel_urls, setup_logging, custom_frontend
setup_logging()  # Initialize logging configuration
logger = logging.getLogger(__name__)

from tunnels import providers, Tunnel
from helper.subscription import subscriptions
from helper.error import api_error_stopping_tunnel
import concurrent.futures
import flask
from flask import session, request, redirect, url_for, flash
import json
import os
from routes.log import log_bp
from routes.auth import login_required
from flask_apscheduler import APScheduler
from tunnelmgr import stop_one_tunnel, reset_one_tunnel, tunnels, tun_tasks, prepare_tunnels

# tunnels = tunnel_urls

app = flask.Flask(__name__)
app.register_blueprint(log_bp)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')
app.config["SCHEDULER_API_ENABLED"] = True

# scheduler = APScheduler()
from jobs import scheduler
scheduler.init_app(app)
scheduler.start()

@app.route('/favicon.ico')
def fav():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico')

# tun_tasks = [] # this is what we do for CRUD

my_providers = [
    {"id": i, "provider": p, "user_enabled": True} for i, p in enumerate(providers)
]

# https://stackoverflow.com/a/53112659
def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


def serialize(obj):
    obj_dict = obj.__dict__.copy()
    serialized_dict = {}
    for k in obj_dict:
        if is_jsonable(obj_dict[k]):
            serialized_dict[k] = obj_dict[k]
        else:
            serialized_dict[k] = type(obj_dict[k]).__name__
    return serialized_dict

# Start or restart tunnels

def reset_tunnels(scope:str="all"):
    """
    Reset all providers by default, or enabled providers if specified.
    """
    # stop tunnels
    if scope == "all":
        provider_to_reset = providers
    elif scope == "enabled":
        provider_to_reset = [p['provider'] for p in my_providers if p["user_enabled"]]

    for tunnel in tun_tasks:
        if tunnel.provider_instance.__class__ not in provider_to_reset:
            continue
        try:
            tunnel.stop()
        except Exception as e:
            logger.error(f"Error stopping tunnel: {e}")

    for tunnel in tunnels:
        for provider in provider_to_reset:
            logger.info(f"Starting tunnel {tunnel} with provider {provider.__name__}")
            try:
                tunnel_instance = Tunnel(
                    url=tunnel,
                    provider_instance=provider
                )
            except Exception as e:
                logger.error(f"Error starting tunnel: {e}")
                continue
            if tunnel_instance in tun_tasks:
                continue
            else:
                tun_tasks.append(tunnel_instance)
    allowed_tun_tasks = [t for t in tun_tasks if t.provider_instance.__class__ in provider_to_reset]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(tunnel.start): tunnel for tunnel in allowed_tun_tasks}
        for f in concurrent.futures.as_completed(futures):
            tunnel = futures[f]

@app.get("/")
def index():
    # Check if custom index.html exists in public folder
    public_index_path = os.path.join(app.root_path, 'public', 'index.html')
    if os.path.exists(public_index_path) and custom_frontend:
        return flask.send_from_directory('public', 'index.html'), 404
    else:
        # Fallback to default template
        return flask.render_template("index.html"), 404


# Providers
@app.get(f"/{api_password}/providers")
def get_providers():
    serialized_providers = [
        {
            "id": provider["id"],
            "provider": provider["provider"].__name__,
            "user_enabled": provider["user_enabled"]
        } for provider in my_providers
    ]
    return flask.jsonify(serialized_providers)

@app.post(f"/{api_password}/providers/<int:provider_id>")
def toggle_provider(provider_id):
    if provider_id < 0 or provider_id >= len(my_providers):
        return flask.jsonify(
            {
                "msg": "Provider not found",
                "code": "error"
            }
        ), 404
    provider = my_providers[provider_id]
    provider["user_enabled"] = not provider["user_enabled"]
    serialized_provider = {
        "id": provider["id"],
        "provider": provider["provider"].__name__,
        "user_enabled": provider["user_enabled"]
    }
    return flask.jsonify(serialized_provider)

# Get Tunnels
@app.get(f"/{api_password}/tunnels/<int:tunnel_id>")
def get_tunnel(tunnel_id):
    """
    Get tunnel information by ID
    """
    if tunnel_id < 0 or tunnel_id >= len(tun_tasks):
        return flask.jsonify({"msg": "Tunnel not found", "code": "error"}), 404
    tunnel = tun_tasks[tunnel_id]
    return flask.jsonify(
        serialize(tunnel)
    )

@app.get(f"/{api_password}/tunnels")
def get_tunnels():
    """
    Get all tunnels information
    """
    return flask.jsonify(
        [{"id": i, **serialize(t)} for i, t in enumerate(tun_tasks)]
    ), 200


# Remove Tunnels
@app.delete(f"/{api_password}/tunnels/<int:tunnel_id>")
def delete_tunnel(tunnel_id):
    """
    Stop a specific tunnel by ID
    """
    if tunnel_id < 0 or tunnel_id >= len(tun_tasks):
        return flask.jsonify(
            {
                "msg": "Tunnel not found",
                "code": "error"
            }
        ), 404
    tunnel = tun_tasks[tunnel_id]
    try:
        stop_one_tunnel(tunnel)
        return flask.jsonify(
            {
                "msg": "Tunnel stopped and removed", 
                "code": "success"
            }
        ), 200
    except Exception as e:
        return flask.jsonify(
            {
                "msg": "Unable to remove tunnel. Check program logs.",
                "details": str(e),
                "code": "error"
            }
        ), 500

@app.delete(f"/{api_password}/tunnels/all")
def delete_all_tunnels():
    """
    Fully stop all tunnels
    """
    for tunnel in tun_tasks:
        try:
            stop_one_tunnel(tunnel)
        except Exception as e:
            return flask.jsonify(
                {
                    "msg": "Unable to remove all tunnels. Check program logs.",
                    "details": str(e),
                    "code": "error"
                }
            ), 500
    return flask.jsonify(
        {
            "msg": "All tunnels stopped and removed",
            "code": "success"
        }
    ), 200

# Reset Tunnels (remove and start again)
@app.post(f"/{api_password}/tunnels/<int:tunnel_id>")
def reset_tunnel(tunnel_id):
    """
    Reset a specific tunnel by ID
    """
    if tunnel_id < 0 or tunnel_id >= len(tun_tasks):
        return flask.jsonify({"error": "Tunnel not found"}), 404
    tunnel = tun_tasks[tunnel_id]
    provider_name = tunnel.provider_instance.__class__.__name__
    try:
        tunnel.stop()
    except Exception as e:
        return flask.jsonify(
            {
                "msg": f"Unable to remove {provider_name}, check program logs. {str(e)}",
                "code": "error"
            }
        ), 500
    try:
        tunnel.start()
        return flask.jsonify(
            {
                "msg": "Tunnel has been reset"
            }
        ), 200
    except Exception as e:
        return flask.jsonify(
            {
                "msg": f"Unable to start {provider_name}, check program logs. {str(e)}",
                "details": str(e),
                "code": "error"
            }
        ), 500

@app.post(f"/{api_password}/tunnels")
def reset_all_tunnels():
    """
    Reset all tunnels or tunnels for specific providers.
    """
    request_data = flask.request.get_json()
    providers_to_use = request_data.get("providers", "all")
    try:
        reset_tunnels(scope=providers_to_use)
        return flask.jsonify(
            {"msg": "All tunnels have been reset"}
        ), 200
    except Exception as e:
        return flask.jsonify(
            {
                "msg": f"One or more tunnels could not be reset, check program logs. {str(e)}",
                "code": "error"
            }
        ), 500


@app.route(f"/{api_password}/dashboard")
@login_required
def dashboard():
    return flask.render_template(
        "layout.html",
        api_path=api_password,
        subscription_password=subscription_password,
    )

@app.route(f"/{api_password}/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        
        # Form authentication
        if password == api_password:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password!', 'error')

    return flask.render_template("login.html")

@app.route(f"/{api_password}/logout")
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.get(f"/{subscription_password}/subscription")
def subscription():
    subscription_list = [url for p in subscriptions.values() for url in p.values()]
    subscription_content = "\n".join(subscription_list)
    return flask.render_template(
        "subscription.txt",
        content=subscription_content
    )

if __name__ == "__main__":
    prepare_tunnels()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False) 