#! coding:utf-8
#! /usr/bin/python
import requests,json,time,logging,redis,random,pymysql

class logging_record:
    '''记录日志'''
    def record_message(self,message,status):
        '''记录日志格式'''
        logging.basicConfig(level=logging.INFO, filename='out.txt',format='%(levelname)s  -%(asctime)s  -%(lineno)d - %(message)s')
        if not status:
            logging.error('【Zabbix】 {ser} 请求错误'.format(ser=message))
        else:
            logging.info('【Zabbix】  {ser} 请求正常'.format(ser=message))


class SendMessageWX:
    '''发送告警信息到企业微信接口'''
    def __init__(self):
        self.ChatId = "wrlv9XDAAAfox_DcrdhMYoVxFFIFwi7w"
        self.TokenURL="https://api.njtuling.com/workweixin/access-token/get"
        self.SendURL="https://api.njtuling.com/workweixin/appchat/send"
        self.TokenDate={"corp_code": "SIGO", "agent_code": "SIGO_ERP"}

    def Send_Message(self,data_info):
        res = json.loads(requests.post(url=self.TokenURL, json=self.TokenDate).text)
        data=\
        {
                "access_token": res["access_token"],
                "chatid": self.ChatId,
                "msgtype": "text",
                "text":
                        {"content":data_info}
        }
        # json.loads(requests.post(url=self.SendURL,json=data).text)
        return "{data}告警发送成功".format(data=data_info)


def Get_Http_status(server,url,pattern,data):
    '''通过Get或Post请求获取返回的Http状态码'''
    global res
    start_time = time.time()
    if pattern == "get":
        res = requests.get(url)
    elif pattern== "post":
        res = requests.post(url=url,json=json.loads(data))
    # res=res.text.encode('utf-8').decode('unicode-escape')
    spend_time= round(time.time()-start_time, 3)
    if not int(res.status_code) == 200:
        logging_record().record_message(SendMessageWX().Send_Message('{server} 接口调用失败 ,总共耗时{spend}'.format(server=server,spend=spend_time)),status=False)
    else:
        logging_record().record_message('{server} 接口调用正常，总共耗时{spend}'.format(server=server,spend=spend_time),status=True)


class Redis_Connect:
        def __init__(self,host):
            self.connection = redis.StrictRedis(host=host,port=6379,db=1,decode_responses=True)
            self.num=random.randint(1,20)
        def Redis_exist(self):
            # self.connection.hmget('stock_402983913259008_442585113984142_445458900223488_1',['physical_stock'])
            if self.connection.hexists('stock_402983913259008_442585113984142_445458900223488_1','physical_stock'):
                self.connection.hmset('stock_402983913259008_442585113984142_445458900223488_1',{'physical_stock':self.num})
                print(self.num)
                return self.num


class Mysql_Connect:
        def __init__(self,host,username,password,db):
            self.connection=pymysql.connect(host,username,password,db)
            self.host=host
            self.cursor=self.connection.cursor()
        def Comment(self,order):
            self.cursor.execute("{}".format(order))
            data  = self.cursor.fetchone()
            self.cursor.close()
            print(data[0])
            return data[0]
        def Compare_Good(self):
            num = Redis_Connect('10.0.180.249').Redis_exist()
            time.sleep(1)
            if self.Comment("SELECT physical_stock FROM sto_warehouse_sku_stock WHERE id='451965683419524';") != num:
                logging_record().record_message(SendMessageWX().Send_Message('【Zabbix】 {host} redis 同步失败，请及时确认。 '.format(host=self.host)))


if __name__ == "__main__":

    # Get_Http_status('物流查询','https://api.njtuling.com/logistics/search','post','{"billnum":"9880416657103","company":"邮政小包","appkey":"sigo.erp","appsecret":"5d8008ed26634fadae48f2849a0d1c8d"}')
    # Get_Http_status('短信发送', 'https://api.njtuling.com/sms/note/sendtrigger','post','{"appCode": "erp","message": "test","sign": "视客眼镜网","phone": "15960375989"}')
    # Get_Http_status('地区获取','https://api.njtuling.com/area/district/getbystep?appcode=sigo.b2b&step=2','get','')
    # Get_Http_status('地区IP+端口接口测试', 'http://10.0.150.39:8200/district/getbystep?appcode=sigo.b2b&step=2', 'get', '')
    # Mysql_Connect('10.0.180.29','saascangpei','sigo@123','saascangpei').Comment("{order}".format(order=str("SELECT physical_stock FROM sto_warehouse_sku_stock")))
    Mysql_Connect('10.0.180.29','saascangpei','sigo@123','saascangpei').Compare_Good()