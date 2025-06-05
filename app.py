from flask import Flask, render_template, request, jsonify
import meraki
import os

app = Flask(__name__)

MERAKI_API_KEY = 'a64475ed0b2786f739ae12d4ee2dbb6247b59cb5'
DASHBOARD = meraki.DashboardAPI(MERAKI_API_KEY, suppress_logging=True)
ORG_ID = None

HOTEL_PREFIXES = {
    'RPS': 'Royal Palm',
    'CAS': 'Cannonier',
    #'HO': 'Head Office',
    'MAS': 'Mauricia',
    'SHS': 'Shandrani',
    'TBS': 'Trou aux Biches'
}


def get_meraki_devices():
    try:
        global ORG_ID
        if not ORG_ID:
            orgs = DASHBOARD.organizations.getOrganizations()
            ORG_ID = orgs[0]['id']

        status_list = DASHBOARD.organizations.getOrganizationDevicesStatuses(ORG_ID)
        status_lookup = {dev['serial']: dev['status'] for dev in status_list}

        networks = DASHBOARD.organizations.getOrganizationNetworks(ORG_ID)
        all_devices = []

        for net in networks:
            devices = DASHBOARD.networks.getNetworkDevices(net['id'])
            for device in devices:
                serial = device.get('serial')
                name = device.get('name') or device.get('model') or 'Unnamed'
                status = status_lookup.get(serial, 'Unknown')

                hotel_name = 'Other'
                for prefix, hotel in HOTEL_PREFIXES.items():
                    if name and name.startswith(prefix):
                        hotel_name = hotel
                        break

                device_type = 'Other'
                if 'SW' in name.upper():
                    device_type = 'Switch'
                elif 'AP' in name.upper():
                    device_type = 'Access Point'

                all_devices.append({
                    'Name': name,
                    'Status': status,
                    'Hotel': hotel_name,
                    'Type': device_type
                })

        return sorted(all_devices, key=lambda x: (x['Hotel'], x['Name']))

    except Exception as e:
        return [{'Name': 'Error', 'Status': f'Meraki API error: {str(e)}', 'Hotel': 'Error', 'Type': 'Error'}]


@app.route('/', methods=['GET', 'POST'])
def index():
    selected_hotel = request.form.get('hotel', '')
    filter_status = request.form.get('status', '')
    selected_type = request.form.get('type', '')

    system_data = get_meraki_devices()

    hotels = sorted(set(d['Hotel'] for d in system_data))
    statuses = sorted(set(d['Status'] for d in system_data))
    types = sorted(set(d['Type'] for d in system_data))

    if selected_hotel:
        system_data = [d for d in system_data if d['Hotel'] == selected_hotel]
    if filter_status:
        system_data = [d for d in system_data if d['Status'].lower() == filter_status.lower()]
    if selected_type:
        system_data = [d for d in system_data if d['Type'] == selected_type]

    return render_template('index.html',
                           system_data=system_data,
                           hotels=hotels,
                           statuses=statuses,
                           types=types,
                           selected_hotel=selected_hotel,
                           filter_status=filter_status,
                           selected_type=selected_type)


@app.route('/api/devices/meraki', methods=['GET'])
def api_meraki_devices():
    return jsonify(get_meraki_devices())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
