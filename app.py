from flask import Flask, render_template, request, jsonify
import meraki

app = Flask(__name__)

MERAKI_API_KEY = 'a64475ed0b2786f739ae12d4ee2dbb6247b59cb5'
DASHBOARD = meraki.DashboardAPI(MERAKI_API_KEY, suppress_logging=True)
ORG_ID = None

def get_meraki_devices():
    try:
        global ORG_ID
        if not ORG_ID:
            orgs = DASHBOARD.organizations.getOrganizations()
            ORG_ID = orgs[0]['id']

        # Get device statuses
        status_list = DASHBOARD.organizations.getOrganizationDevicesStatuses(ORG_ID)
        status_lookup = {dev['serial']: dev['status'] for dev in status_list}

        # Get all networks and devices
        networks = DASHBOARD.organizations.getOrganizationNetworks(ORG_ID)
        all_devices = []

        for net in networks:
            devices = DASHBOARD.networks.getNetworkDevices(net['id'])
            for device in devices:
                serial = device.get('serial')
                status = status_lookup.get(serial, 'Unknown')

                all_devices.append({
                    'Name': device.get('name', device['model']),
                    'Status': status
                })

        sorted_devices = sorted(all_devices, key=lambda x: (x.get('Name') or '', x.get('Status') or ''))
        return sorted_devices

    except Exception as e:
        return [{'Name': 'Error', 'Status': f'Meraki API error: {str(e)}'}]

# Web interface
@app.route('/', methods=['GET', 'POST'])
def index():
    filter_status = request.form.get('status', '')
    system_data = get_meraki_devices()

    if filter_status:
        system_data = [d for d in system_data if d['Status'].lower() == filter_status.lower()]

    return render_template('index.html',
                           system_data=system_data,
                           selected_system='Meraki',
                           filter_status=filter_status)

# API route
@app.route('/api/devices/meraki', methods=['GET'])
def api_meraki_devices():
    return jsonify(get_meraki_devices())

if __name__ == '__main__':
    app.run(debug=True)
