# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.addons.ho_moadian.models.moadian.api  import TaxApi
from odoo.exceptions import ValidationError

import base64
from datetime import datetime
import math

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'


    mod_tax_id = fields.Char('Moadian Tax ID',tracking=True) 
    mod_ir_tax_id = fields.Char('Moadian Refrence Tax ID') 

    mod_uid = fields.Char('Moadian UID') 
    mod_reference_number = fields.Char('Moadian Reference Number') 
    mod_status = fields.Selection([
            ('draft', '_'),
            ('PENDING', 'PENDING'),
            ('FAILED', 'FAILED'),
            ('SUCCESS', 'SUCCESS'),
            ('IN_PROGRESS', 'IN_PROGRESS'),
            ('NOT_FOUND', 'NOT_FOUND'),
        ],string='Modaian Status',readonly=True,copy=False,tracking=True,default='draft')


    mod_inty = fields.Selection([('1', 'Type1'),('2', 'Type2'),('3', 'Type3')],string='Modaian Invoice Type', default='1')
    #mod_inno = fields.Char('Moadian Invoice Number',readonly=True) 
    mod_inp =  fields.Selection([('1', 'Sale'),('2', 'Foroush Arzi'),('3', 'Tala'),('4', 'Peymankari'),('5', 'Khadamati'),('6', 'Havapeyma')],string='Modaian Invoice Pattern', default='1')
    
    mod_ins = fields.Selection([('1', 'Main'),('2', 'Corrective'),('3', 'Cancellation'),('4', 'Return_sale')],string='Modaian Invoice Subject', default='1',tracking=True)

    mod_serial_number=fields.Char ('Modian Serial Number',compute='_compute_mod_serial',default=lambda self: self.id,store=True,readonly=False,tracking=True)

    @api.depends('state')
    def _compute_mod_serial(self):

        for record in self:
           print ("ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
           print (record.id)
           if record.mod_serial_number ==False:
                record.mod_serial_number=record.id
    
    def inquery_moadian(self):
       
        filecontent = base64.b64decode( self.env.user.company_id.pkey_file)
        org_api = TaxApi(
                private_key=filecontent,
                fiscalId= self.env.user.company_id.fiscal_id,
                api_url= self.env.user.company_id.org_api_url,
                economic_code=self.env.user.company_id.vat)

        print( org_api.get_server_information())
        
        #print (org_api.get_token())

        print ("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRrr")
        print (self.mod_reference_number)


        
        
        
        for rec in self:
            a=org_api.get_inquiry_by_reference_number(self.mod_reference_number)
            print ( a['result']['data'][0])
            data=a['result']['data'][0]
            status=data['status']
            rec.write({'mod_status':status})
            rec.message_post(body= str(data))
            #rec.message_post(body= str(json.dumps(a['result']['data'][0],ensure_ascii=False)))
        

    def send_moadian(self):

        filecontent = base64.b64decode( self.env.user.company_id.pkey_file)
        org_api = TaxApi(
                private_key=filecontent,
                fiscalId= self.env.user.company_id.fiscal_id,
                api_url= self.env.user.company_id.org_api_url,
                economic_code=self.env.user.company_id.vat)
        
        
       # print(self.invoice_date.timestamp())
        dt = datetime.combine(self.invoice_date, datetime.min.time())
        ts = datetime.timestamp(dt)
        
       
        bodies=[]
        tvam=0
        tdis=0

        tprdis=0
        tadis=0
        

     
        
        
        for line in self.line_ids:
        
            if (line.product_id.id):

                prdis = line.quantity * line.price_unit 
                dis=math.floor(line.quantity * (line.price_unit * line.discount/100))
                adis= prdis-dis

                vra=0
                
                print (line.tax_ids)
                for tax in line.tax_ids:
                    print (tax.amount)
                    vra=tax.amount
                
                vam=math.floor(adis *  vra/100)
                tsstam= adis+ vam
                
               

               
                


                if not int(line.product_id.mod_id):
                    raise ValidationError("This Product: "+ line.name + " has not valid moadian ID")


                bodies.append ({
                    "sstid": line.product_id.mod_id,
                    "sstt": line.name,
                    # "sstt": "Selling Telobal cloud communication system software package",
                    "am": line.quantity,
                    "fee": line.price_unit,
                    "prdis": prdis ,
                    "dis": dis,
                    "adis": adis,
                    "vra": vra,
                    "vam":vam,
                    "tsstam": tsstam,
                })
                
                tdis+=dis
                tvam+=vam

                tprdis+=prdis
                tadis+=adis
        
        irtaxid=None
        if self.mod_ir_tax_id and self.mod_ir_tax_id!='1':
            irtaxid=self.mod_ir_tax_id
       
        packet=[]
        if self.partner_id.mod_top == '1':
            packet = [{
            "serial_number" : self.mod_serial_number,
            "uid" : self.mod_serial_number,
            "header" : {
                "taxid": None,
                "indatim": int( ts * 1000),
                "inno": f"{self.id:#0{12}x}"[2:],
                "inty": self.mod_inty,
                "irtaxid": irtaxid,
                "inp": self.mod_inp,
                "ins": self.mod_ins,
                "tins": self.env.user.company_id.vat,
                "bid": self.partner_id.vat,
                "tob":self.partner_id.mod_top,
                "setm":"1",
                
                "tprdis": tprdis,
                "tdis": tdis,
                "tadis":tadis,
                "tvam": tvam,
                "todam": "0",
                "tbill": tadis+tvam,
               
            },
            "body" : bodies,
            "payment" : [{}],
            "extension" : [{}]
           }]
        
        else:

            packet = [{
            "serial_number" : self.mod_serial_number,
            "uid" : self.mod_serial_number,
            "header" : {
                "taxid": None,
                "indatim": int( ts * 1000),
                "inno": f"{self.id:#0{12}x}"[2:],
                "inty": self.mod_inty,
                "irtaxid": irtaxid,
                "inp": self.mod_inp,
                "ins": self.mod_ins,
                "tins": self.env.user.company_id.vat,
                "tinb": self.partner_id.vat,
                "tob":self.partner_id.mod_top,
                "setm":"1",
                
                "tprdis": tprdis,
                "tdis": tdis,
                "tadis":tadis,
                "tvam": tvam,
                "todam": "0",
                "tbill": tadis+tvam,
               
            },
            "body" : bodies,
            "payment" : [{}],
            "extension" : [{}]
            }]





   
        print (packet)

        #return

        a = org_api.send_invoice(packet)
        print (a)

        data=a[0]['result']   
        rf=data[0]['referenceNumber']
        uti=a[1][0]['unique_tax_id']

        for rec in self:
            rec.write({'mod_reference_number':rf,'mod_tax_id':uti})
            rec.message_post(body= str(data))