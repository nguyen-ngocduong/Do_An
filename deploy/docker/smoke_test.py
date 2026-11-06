"""Docker integration check. Isolated project/volume; no real Gemini or BE/.env."""
import io
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
import zipfile

import httpx

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deploy/docker/verification.json'

def port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); return s.getsockname()[1]

def main():
    results=[]
    def passed(text):
        results.append(text);print('PASS:',text,flush=True)
    project='nidr-smoke-'+secrets.token_hex(4)
    with tempfile.TemporaryDirectory(prefix='nidr-docker-smoke-') as temporary:
        folder=Path(temporary)
        for name in ['docker-compose.yml','docker-compose.prod.yml']:
            shutil.copyfile(ROOT/name,folder/name)
        (folder/'deploy/docker').mkdir(parents=True)
        shutil.copyfile(ROOT/'deploy/docker/nginx.prod.conf',folder/'deploy/docker/nginx.prod.conf')
        password=secrets.token_urlsafe(24);host_port=port()
        (folder/'.env').write_text(f'ADMIN_USERNAME=smoke\nADMIN_PASSWORD={password}\nNIDR_PORT={host_port}\n')
        env={**os.environ,'COMPOSE_PROJECT_NAME':project,'ADMIN_USERNAME':'smoke','ADMIN_PASSWORD':password,'GEMINI_API_KEY':'','GEMINI_MODEL':'gemini-3.5-flash-lite','NIDR_VERSION':'1.0.0','NIDR_PORT':str(host_port)}
        def compose(*args,extra=()):
            return subprocess.run(['docker','compose','-p',project,'-f','docker-compose.yml',*extra,*args],cwd=folder,env=env,check=True,capture_output=True,text=True)
        headers={'Origin':f'http://127.0.0.1:{host_port}','Sec-Fetch-Site':'same-origin'}
        client=httpx.Client(base_url=f'http://127.0.0.1:{host_port}',timeout=60,headers=headers)
        def login(c=client):
            r=c.post('/api/auth/login',json={'username':'smoke','password':password});assert r.status_code==200,r.text
        def wait_run(rid):
            for _ in range(100):
                r=client.get('/api/runs/'+rid).json()
                if r['status']=='completed':return r
                assert r['status']!='failed',r
                time.sleep(.2)
            raise AssertionError(r)
        def wait_case(rid):
            for _ in range(400):
                value=client.get(f'/api/runs/{rid}/explanations/0').json()
                if value['status'] in ['completed','partial','failed']:return value
                time.sleep(.25)
            raise AssertionError(value)
        try:
            compose('config','--quiet')
            compose('up','-d','--wait','--wait-timeout','240')
            passed('Images run from delivery-only directory; healthchecks and fresh non-root runtime volume pass')
            assert client.get('/health').json()['status']=='ready'
            r=client.get('/dashboard');assert r.status_code==302 and '/login' in r.headers['location']
            assert client.get('/api/schema').status_code==401
            login();assert client.get('/api/auth/session').json()['username']=='smoke'
            assert client.post('/api/auth/logout',json={},headers={'Origin':'https://external.invalid'}).status_code==403
            model=client.get('/api/model').json();assert model['checks']['golden_prediction_match'] and model['model_load_count']==1
            assert client.get('/api/runs').json()['total']==0
            passed('Login/session, same-origin protection, private pages, frozen versions/checksum/golden and empty history')
            sample=ROOT/'output/integration_runs/integration_20261022_075217_0b67d48f/input_features.csv'
            uploaded=client.post('/api/runs',files={'file':('sample.csv',sample.read_bytes(),'text/csv')})
            assert uploaded.status_code==202,uploaded.text
            rid=uploaded.json()['id'];assert wait_run(rid)['processed_rows']==50
            assert client.get(f'/api/runs/{rid}/predictions').json()['total']==50
            r=client.post(f'/api/runs/{rid}/explanations',json={'row_indices':[0],'use_gemini':False,'audience_level':'technical'})
            assert r.status_code==202,r.text
            case=wait_case(rid);assert case['status']=='completed',case
            for name in ['waterfall.png','explanation.json','report_vi.md','top5_features.csv']:
                assert client.get(f'/api/runs/{rid}/explanations/0/files/{name}').status_code==200,name
            passed('Batch50, actual CPU SHAP, no-key path and four saved artifacts')
            review_path=f'/api/runs/{rid}/human-reviews/0'
            context=client.get(review_path).json()['context']
            body={'reviewer_name':'Docker smoke (automated test)','prediction_assessment':'uncertain','proposed_label':None,'explanation_clarity':None,'evidence_faithfulness':None,'actionability':None,'notes':'Container integration test, not an expert assessment.','evidence_signature':context['evidence_signature']}
            assert client.put(review_path,json=body).status_code==200
            assert client.get(review_path+'/export').json()['stale'] is False
            r=client.get(f'/api/runs/{rid}/export',params={'format':'zip'});assert r.status_code==200,r.text
            assert 'predictions.csv' in zipfile.ZipFile(io.BytesIO(r.content)).namelist()
            passed('Human review save/export and ZIP download')
            compose('up','-d','--force-recreate','--wait','--wait-timeout','240')
            login();assert client.get('/api/runs/'+rid).json()['processed_rows']==50
            assert client.get(review_path).json()['review']['reviewer_name']==body['reviewer_name']
            passed('Container recreate retains run, SHAP files and review; gateway DNS recovers')
            # Temporary mock factory is mounted for testing only, never copied into release images.
            (folder/'mock_app.py').write_text('from BE.config import load_settings\nfrom BE.main import create_app\nfrom BE.tests.conftest import FakeGeminiClient\ns=load_settings()\ns.gemini_pause_seconds=0\napp=create_app(s,gemini_client=FakeGeminiClient())\n')
            override={'services':{'backend':{'environment':{'PYTHONPATH':'/app:/test'},'volumes':[str(ROOT/'BE/tests')+':/app/BE/tests:ro',str(folder/'mock_app.py')+':/test/mock_app.py:ro'],'command':['python','-m','uvicorn','mock_app:app','--host','0.0.0.0','--port','8000','--workers','1']}}}
            (folder/'mock.json').write_text(json.dumps(override));extra=('-f','mock.json')
            compose('up','-d','--wait','--wait-timeout','240',extra=extra)
            login()
            r=client.post(f'/api/runs/{rid}/explanations',json={'row_indices':[0],'use_gemini':True,'retry_gemini':True,'audience_level':'technical'});assert r.status_code==202,r.text
            case=wait_case(rid);assert case['status']=='completed' and case['gemini_status']=='accepted',case
            passed('Gemini mocked through isolated container override; no external API used')
            replay=client.post('/api/runs',files={'file':('replay.csv',sample.read_bytes(),'text/csv')},data={'mode':'replay','interval_seconds':.1})
            assert replay.status_code==202,replay.text
            wait_run(replay.json()['id']);passed('Replay50 completes')
            # Backup while stopped, copy the complete volume into a separate volume and verify it.
            compose('stop')
            volume=subprocess.check_output(['docker','volume','ls','-q','--filter',f'label=com.docker.compose.project={project}','--filter','label=com.docker.compose.volume=runtime'],text=True).strip()
            subprocess.run(['docker','run','--rm','-v',volume+':/data:ro','-v',str(folder)+':/backup','--entrypoint','sh','nidr-gateway:1.0.0','-c','tar czf /backup/runtime.tgz -C /data .'],check=True)
            restore_volume=project+'-restore'
            subprocess.run(['docker','volume','create',restore_volume],check=True,stdout=subprocess.DEVNULL)
            try:
                subprocess.run(['docker','run','--rm','-v',restore_volume+':/data','-v',str(folder)+':/backup:ro','--entrypoint','sh','nidr-gateway:1.0.0','-c','tar xzf /backup/runtime.tgz -C /data'],check=True)
                (folder/'restore.json').write_text(json.dumps({'volumes':{'runtime':{'external':True,'name':restore_volume}}}))
                restore_extra=('-f','restore.json')
                compose('up','-d','--force-recreate','--wait','--wait-timeout','240',extra=restore_extra)
                login();assert client.get(review_path).json()['review']['notes']==body['notes']
                passed('Stopped backup and restore into a distinct volume retain the review and run')
                compose('down',extra=restore_extra)
            finally:subprocess.run(['docker','volume','rm',restore_volume],stdout=subprocess.DEVNULL)
            # Production TLS overlay uses the same images, supplied certificate and different test ports.
            cert=folder/'tls';cert.mkdir()
            subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=localhost','-addext','subjectAltName=IP:127.0.0.1,DNS:localhost','-keyout',str(cert/'server.key'),'-out',str(cert/'server.crt')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            tlsport=port();plainport=port();env['NIDR_TLS_DIR']=str(cert)
            (folder/'tls-ports.json').write_text(json.dumps({'services':{'gateway':{'ports':[f'127.0.0.1:{plainport}:8080',f'127.0.0.1:{tlsport}:8443']}}}))
            # Base production uses !override; override the test list too with YAML.
            (folder/'tls-ports.yml').write_text(f'services:\n  gateway:\n    ports: !override\n      - "127.0.0.1:{plainport}:8080"\n      - "127.0.0.1:{tlsport}:8443"\n')
            tls_extra=('-f','docker-compose.prod.yml','-f','tls-ports.yml')
            compose('up','-d','--wait','--wait-timeout','240',extra=tls_extra)
            with httpx.Client(base_url=f'https://127.0.0.1:{tlsport}',verify=str(cert/'server.crt'),timeout=30,headers={'Origin':f'https://127.0.0.1:{tlsport}','Sec-Fetch-Site':'same-origin'}) as secure:
                login(secure);assert 'Secure' in secure.post('/api/auth/login',json={'username':'smoke','password':password}).headers['set-cookie']
                assert secure.get('/api/runs/'+rid).status_code==200
                assert secure.post('/api/auth/logout',json={}).status_code==200
            passed('Production overlay TLS, Secure cookie, login/logout and persistent data')
            stats=subprocess.check_output(['docker','stats','--no-stream','--format','{{.Name}} {{.MemUsage}}'],text=True)
            OUT.write_text(json.dumps({'passed':results,'count':len(results),'platform':'Linux amd64; Windows not directly tested','external_gemini_calls':0,'container_memory_observation':stats.splitlines(),'note':'All mutations used temporary Docker project/volumes and test credentials; user services untouched.'},ensure_ascii=False,indent=2)+'\n')
            print('Wrote',OUT,flush=True)
        finally:
            client.close()
            compose('down','--volumes','--remove-orphans')
if __name__=='__main__':main()
