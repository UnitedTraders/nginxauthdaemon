# nginxauthdaemon

[![Snyk](https://snyk.io/test/github/UnitedTraders/nginxauthdaemon/badge.svg)](https://snyk.io/test/github/UnitedTraders/nginxauthdaemon/)

Authentication daemon for nginx-proxied or nginx-served applications.

## Installation and Configuration

1. Create virtual environment for the daemon: `virtualenv env`
2. Activate it: `. ./env/bin/activate`
3. Install dependencies: `pip install -r requirements.txt -r requirements-run.txt`
4. Create config file overriding default values, see [Daemon Configuration](#daemon-configuration). **NB!** You need to override default `SESSION_SALT` and `DES_KEY` for security.
5. Setup env variable `DAEMON_SETTINGS` pointing to your config file.
6. Run daemon with your favorite WSGI server, e.g. `gunicorn nginxauthdaemon:app`.
7. Update nginx.conf. See [NGINX Configuration](#nginx-configuration).
8. Reload nginx (`nginx -t reload`).
9. Test your setup.

## Docker

- Build: `docker build -t nginxauthdaemon .`
- Launch: `docker run -p 5000:5000 -v $(pwd)/example.cfg:/example.cfg -e DAEMON_SETTINGS=/example.cfg -e WEB_CONCURRENCY=4 nginxauthdaemon`
- Compose file located in `docker-compose.yml.sample`

## Development Setup

### Prerequisites

```bash
virtualenv env && . ./env/bin/activate
pip install -r requirements.txt
pip install -r requirements-run.txt
```

### SpecKit (AI-assisted development)

This project uses [SpecKit](https://speckit.dev) for AI-assisted specification, planning, and task management. To set up the development environment with SpecKit:

1. Install the SpecKit CLI integration for your AI coding assistant (Claude Code, Copilot CLI, etc.).
2. The `.specify/` directory contains project templates and the constitution — these are not committed to the repository.
3. Run `/speckit-constitution` to initialize project principles on a fresh clone.
4. Use `/speckit-specify`, `/speckit-plan`, and `/speckit-tasks` for feature development workflows.

### Running Locally

```bash
DAEMON_SETTINGS=/path/to/config.cfg python -m nginxauthdaemon.nginxauthdaemon
# Or with gunicorn:
DAEMON_SETTINGS=/path/to/config.cfg gunicorn -b 0.0.0.0:5000 -k eventlet nginxauthdaemon:app
```

## Daemon Configuration

Basic configuration properties:

| Option | Description |
|--------|-------------|
| `REALM_NAME` | Realm name shown on login page |
| `SESSION_COOKIE` | Session cookie name. Typically you do not need to change this. |
| `TARGET_HEADER` | Header used to pass protected URL from NGINX |
| `SESSION_SALT` | Long string used as salt for creation of session key. |
| `DES_KEY` | 8-byte DES encryption key |
| `AUTHENTICATOR` | Authenticator class name, by default `auth.DummyAuthenticator` |

### Authenticators

Available out-of-the-box:

| Authenticator | Description |
|---------------|-------------|
| `nginxauthdaemon.auth.DummyAuthenticator` | Simplest authenticator checking username equals password |
| `nginxauthdaemon.crowdauth.CrowdAuthenticator` | Atlassian Crowd based authenticator |

Crowd authenticator additional options:

| Option | Description |
|--------|-------------|
| `CROWD_URL` | Crowd server URL, e.g. `http://localhost:8095/crowd/` |
| `CROWD_APP_NAME` | Crowd application name |
| `CROWD_APP_PASSWORD` | Crowd application password |

### Access Token Options

| Option | Description |
|--------|-------------|
| `JWT_PRIVATE_KEY` | RS256 secret key for access token signing |
| `ACCESS_TOKEN_COOKIE` | Access token cookie name |

## NGINX Configuration

Your NGINX should be compiled with `ngx_http_auth_request_module`. Check using `nginx -V`.

Example configuration:

```nginx
upstream auth-backend {
    server 127.0.0.1:5000;
}

location = /auth/validate {
    internal;
    proxy_pass http://auth-backend;

    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
}

location = /auth/login {
    proxy_pass http://auth-backend;
    proxy_set_header X-Target $request_uri;
}

# Protected application
location / {
    auth_request /auth/validate;

    # redirect 401 and 403 to login form
    error_page 401 403 =200 /auth/login;
}
```

## HAProxy Configuration

Install `haproxy-auth-request` script from https://github.com/TimWolla/haproxy-auth-request/

Sample HAProxy config (thanks to Dmitry Kamenskikh):

```haproxy
global
        log /dev/log        local0
        log /dev/log        local1 notice
        chroot /var/lib/haproxy
        stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
        stats timeout 30s
        user haproxy
        group haproxy
        daemon

        lua-load /usr/share/haproxy/auth-request.lua

defaults
        log        global
        mode        http
        option        httplog
        option        dontlognull
        timeout connect 5000
        timeout client  50000
        timeout server  50000

frontend main
        mode http
        bind :80

        acl management path_beg /management
        acl login_page path -i /auth/login
        http-request lua.auth-request auth_request /auth/validate if management
        acl login_success var(txn.auth_response_successful) -m bool
        http-request add-header X-target %[path] if management
        http-request set-path /auth/login if management ! login_success
        use_backend auth_request if login_page

        default_backend just200

backend just200
        server main 172.17.0.1:3000 check

backend auth_request
        mode http
        server main 172.17.0.1:5000 check
```

## Limitations

Daemon can be extended to support LDAP or any other auth method, but it supports only Atlassian Crowd for now. PRs with new auth methods are welcome.

## License

The reference implementation is subject to MIT License.
