# fail2ban-frontend
Easy installed frontend for your server

# !! DONT FORGET CREATE JAIL !!
# Steps to install
## req: 0.3 GHz CPU, 0.5 MB Ram, 8 MB HDD
## 1. Connect to server and install libs, git:
`sudo apt install python3-flask python3-geoip2 git`
## 2. Clone this repo:
`git clone https://github.com/PincessWoona/fail2ban-frontend`
## 3. For starting:
```
cd fail2ban-frontend
python3 prod.app.py
```
## 4. If you have error check name of jail or edit:
`output = subprocess.check_output(['fail2ban-client', 'status', 'sshd'], universal_newlines=True)`
to 
`output = subprocess.check_output(['fail2ban-client', 'status', '{!name!}'], universal_newlines=True)`
change {!name!} on your jail name

# Original GeoLite2
https://github.com/wp-statistics/GeoLite2-Country
