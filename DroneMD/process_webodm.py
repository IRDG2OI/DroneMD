import requests, sys, os, glob, json, time
import status_codes
import settings

def process_webodm(folder):
    """
    Process data from DCIM folder and subfolder
    
    This Source Code Form is subject to the terms of the Mozilla 
    Public License, v. 2.0. If a copy of the MPL was not 
    distributed with this file, You can obtain one at 
    https://mozilla.org/MPL/2.0/. 

    Parameters
    ----------
    folder: str
                folder to process
    """
    # Get folder name before DCIM folder
    path = os.path.normpath(folder)
    input = path.split(os.sep)[-2]

    # # List images files (png for masks)
    types = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG")

    images_list = []
    images_list = [os.path.join(root, name)
                 for root, dirs, files in os.walk(path)
                 for name in files
                 if name.endswith(types)]

    if len(images_list) < 2:
        print("Need at least 2 images")
        # sys.exit(1)
    else:
        print("Found {} images".format(len(images_list)))

    res = requests.post(settings.SERVER + '/api/token-auth/', 
                        data={'username': settings.USERNAME,
                            'password': settings.PASSWORD}).json()

    if 'token' in res:
        print("Logged-in!")
        token = res['token']

        res = requests.post(settings.SERVER + '/api/projects/', 
                            headers={'Authorization': 'JWT {}'.format(token)},
                            data={'name': input }).json()
        if 'id' in res:
            print("Created project: {}".format(res)) 
            project_id = res['id']

            images = [('images', (os.path.basename(file), open(file, 'rb'), 'image/jpg')) for file in images_list]
            options = json.dumps([
                {'name': "orthophoto-resolution", 'value': 1},
                {'name': "auto-boundary", 'value': True},
                # {'name': "auto-boundary-distance", 'value': 50},
                # {'name': "camera-lens", 'value': 'brown'},
                # {'name': "crop", 'value': '0'},
                {'name': "dem-resolution", 'value': '2.0'},
                {'name': "dsm", 'value': True}
                # {'name': "ignore-gsd", 'value': True},
                # {"name": "pc-quality", "value": 'high'},
                # {'name': "resize_to", 'value': 2048},
                # {'name': "rolling-shutter", 'value': True},
                # {'name': "rolling-shutter-readout", 'value': 56},
                # {'name': "use-fixed-camera-params", 'value': True}
            ])
            res = requests.post(settings.SERVER + '/api/projects/{}/tasks/'.format(project_id), 
                        headers={'Authorization': 'JWT {}'.format(token)},
                        files=images,
                        data={
                            'options': options
                        }).json()

            print("Created task: {}".format(res))
            task_id = res['id']
            
            # Change task name to folder name: same as project name
            requests.patch(settings.SERVER + '/api/projects/{}/tasks/{}/'.format(project_id, task_id),
                            headers={'Authorization': 'JWT {}'.format(token)},
                            data={'name': input }).json()

        else:
            print("Cannot create project: {}".format(res))
    else:
        print("Invalid credentials!")

    return res

def check_process(project_id, task_id):
    """
    Monitor runing task in WebODM

    Parameters
    ----------
    project_id: int
                id of project
    task_id: int
                uuid of task
    """
    res = requests.post(settings.SERVER + '/api/token-auth/', 
                        data={'username': settings.USERNAME,
                            'password': settings.PASSWORD}).json()
    if 'token' in res:
        print("Logged-in!")
        token = res['token']    
        res = requests.get(settings.SERVER + '/api/projects/{}/tasks/{}/'.format(project_id, task_id), 
                         headers={'Authorization': 'JWT {}'.format(token)}).json()
    if res['status'] == status_codes.COMPLETED:
        return "Task has completed!"
        #  break
    elif res['status'] == status_codes.FAILED:
        tf = "Task failed: {}".format(res)
        # print("Cleaning up...")
        nr = "No results: bad dataset or bad processing options"
        #requests.delete(settings.SERVER + "/api/projects/{}/".format(project_id), 
        #    headers={'Authorization': 'JWT {}'.format(token)})
        err = "Data kept on platform, please check on web interface: "+ settings.SERVER
        return tf + " " + nr + " " + err
            # sys.exit(1)
    else:
        seconds = res['processing_time'] / 1000
        if seconds < 0: 
            seconds = 0
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
    

def list_all_projects():
    """
    List all OpenDroneMap projects

    Parameters
    ----------
    None
    """
    res = requests.post(settings.SERVER + '/api/token-auth/', 
                    data={'username': settings.USERNAME,
                          'password': settings.PASSWORD}).json()

    if 'token' in res:
        print("Successfully Logged-in!")
        token = res['token']

        projects = requests.get(settings.SERVER + '/api/projects/', 
                            headers={'Authorization': 'JWT {}'.format(token)}).json()
        print("########")
        print("id", "name", "permissions")
        print("----------")
        ## Raw out:
        proj_id = []
        for i in range(len(projects)):
            proj_id.append(projects[i]['id'])
            print(projects[i]['id'], projects[i]['name'])

    else:
        print("Invalid credentials!")
    return projects
