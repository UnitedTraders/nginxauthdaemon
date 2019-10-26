nginxauthdaemon
===============

Authentication daemon for nginx-proxied or nginx-served applications. 

Installation and Configuration
------------------------------

1. Create virtual environment for the daemon ``virtualenv env``

2. Activate it using ``. ./env/bin/activate``

3. Install nginxauthdaemon from pypi ``pip install nginxauthdaemon``

4. Create config file overriding default values, see [Daemon configuration]. *NB!* You need to override default ``SESSION_SALT``, ``DES_IV`` and ``DES_KEY`` for security.

5. Setup env variable ``DAEMON_SETTINGS`` pointing to your config file.

6. Run daemon with your favorite WSGI server, for ex ``gunicorn nginxauthdaemon:app``.

7. Update nginx.conf. See [NGINX Configuration].

8. Reload nginx (``nginx -t reload``).

9. Test your setup.

Docker
------------------------------

* Build: ``docker build -t nginxauthdaemon .``

* Launch: ``docker run -p 5000:5000 -v $(pwd)/example.cfg:/example.cfg -e DAEMON_SETTINGS=/example.cfg -e WEB_CONCURRENCY=4 nginxauthdaemon``

* Compose file located in ``docker-compose.yml.sample``

Daemon configuration
--------------------

Basic configuration properties are:

+----------------+----------------------------------------------------------------+
| Option         | Description                                                    |
+================+================================================================+
| REALM_NAME     | Realm name shown on login page                                 |
+----------------+----------------------------------------------------------------+
| SESSION_COOKIE | Session cookie name. Typically you do not need to change this. |
+----------------+----------------------------------------------------------------+
| TARGET_HEADER  | Header used to pass protected URL from NGINX                   |
+----------------+----------------------------------------------------------------+
| SESSION_SALT   | Long string used a salt for creation of session key.           |
+----------------+----------------------------------------------------------------+
| DES_IV         | 8byte initial vector for DES algorithm                         |
+----------------+----------------------------------------------------------------+
| DES_KEY        | 8byte DES encryption key                                       |
+----------------+----------------------------------------------------------------+
| AUTHENTICATOR  | Authenticator class name, by default 'auth.DummyAuthenticator' |
+----------------+----------------------------------------------------------------+


Authenticators available out-of-the-box:

+----------------------------------------------+----------------------------------------------------------+
| Authenticator name                           | Description                                              |
+==============================================+==========================================================+
| nginxauthdaemon.auth.DummyAuthenticator      | Simplest authenticator checking username equals password |
+----------------------------------------------+----------------------------------------------------------+
| nginxauthdaemon.crowdauth.CrowdAuthenticator | Atlassian Crowd based authenticator                      |
+----------------------------------------------+----------------------------------------------------------+

Crowd authenticator has additional options:

+--------------------+-----------------------------------------------------------+
| Option             | Description                                               |
+====================+===========================================================+
| CROWD_URL          | Crowd server URL, for ex ``http://localhost:8095/crowd/`` |
+--------------------+-----------------------------------------------------------+
| CROWD_APP_NAME     | Crowd application name                                    |
+--------------------+-----------------------------------------------------------+
| CROWD_APP_PASSWORD | Crowd application password                                |
+--------------------+-----------------------------------------------------------+



NGINX Configuration
-------------------

Your NGINX should be compiled with ``ngx_http_auth_request_module``. Please check it using ``nginx -V`` command.

Example configuration::

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

HAProxy Configuration
---------------------

Install `haproxy-auth-request` script from https://github.com/TimWolla/haproxy-auth-request/

Sample HAProxy config (thanks to Dmitry Kamenskikh)::

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

Limitations
-----------

Daemon can be extended to support LDAP or any other auth method, but it support only Atlassian Crowd for now. I'll be happy to merge PRs with new auth methods. 

License
-------

The reference implementation is subject to MIT License.
