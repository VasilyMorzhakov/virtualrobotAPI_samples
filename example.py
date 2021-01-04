import requests
import json
import cv2
import os

def push_frames_encoded(buf_jpg,buf_png,camera):
    buf_json=bytes(json.dumps(camera))
    files=[('files',('1.png',buf_png,'image/png')),
           ('files',('1.jpg',buf_jpg,'image/jpg')),
           ('files',('1.json',buf_json,'application/json'))]
    r = requests.post(url+'/push_frames', files=files)
    if r.status_code!=200:
        raise Exception('could not send files, status code '+str(r.status_code))

def push_frames_cv2(rgb,depth,camera):
    buf_json=bytes(json.dumps(camera))
    _,rgb_bytes=cv2.imencode('.jpg', rgb)
    _,png_bytes=cv2.imencode('.png',depth)
    push_frames_encoded(rgb_bytes,png_bytes,camera)

def request_automated_control(timeout=3):
    r=requests.post(url+'/commands/ask_for_ml_one_shot')
    if r.status_code!=200:
        raise Exception('could not send ask for ml command')
    #wait for response
    r=requests.get(url+'/controls/goto?timeout='+str(timeout))
    if r.status_code==408:
        return None,'timeout occured'
    else:
        if r.status_code==200:
            return r.json(),'ok'
        else:
            return r.text,'error '+str(r.status_code)
def request_manual_control(timeout=120):
    r=requests.post(url+'/commands/ask_for_operator')
    if r.status_code!=200:
        raise Exception('could not send ask for operator command')
    #wait for response
    r=requests.get(url+'/controls/goto?timeout='+str(timeout))
    if r.status_code==408:
        return None,'timeout occured'
    else:
        if r.status_code==200:
            return r.json(),'ok'
        else:
            return r.text,'error '+str(r.status_code)

if __name__=='__main__':
    url=os.environ['API_URL']
    #check connection
    if requests.get(url).status_code==200:
        print('API url responses')
    #list available commands:
    commands=requests.get(url+'/commands/').json()
    print('\nCOMMANDS')
    for c in commands:
        print(c['command']+':')
        print(c['description'])
    #list of possible control responses:
    print('\nPOSSIBLE CONTROL RESPONSES')
    controls=requests.get(url+'/controls/').json()
    for c in controls:
        print(c['control']+':')
        print(c['description'])


    #test API
    print('\nLaunch a sequence')
    with open('data/1.json','r') as f:
        camera=json.load(f)
        print(camera)

    #send files
    push_frames_encoded(open('data/1.jpg','rb'),open('data/1.png','rb'),camera)
    #push_frames_cv2(cv2.imread('data/1.jpg'),cv2.imread('data/1.png',-1),camera)

    #request control frm the ML service
    response=request_automated_control(timeout=2)
    print('automated control: '+str(response))
    #request control from an operator, if the previous command was failed
    response=request_manual_control(timeout=10) #timeout is set to 10s, just to make the script not so long
    print('manual control: '+str(response))




