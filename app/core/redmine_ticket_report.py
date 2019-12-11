#!python
# -*- coding: utf-8 -*-

__version__ = "1"
__author__ = "Junior Andrade"
__email__ = "seisxis@gmail.com"

import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from configparser import ConfigParser


class RedmineTicketReport:
    conn = None
    query = None
    subject = None

    def __init__(self):
        self.connect()
        self.send()

    def connect(self):
        config = self.get_config("database")

        try:
            connect_str = "host='%s' port='%s' dbname='%s' user='%s' password='%s'" \
                          % (config.get("host"),
                             config.get("port"),
                             config.get("database"),
                             config.get("user"),
                             config.get("password"))
            self.conn = psycopg2.connect(connect_str)
        except Exception:
            raise Exception("erro ao conectar no db")

    def send(self):
        message = self.get_message()
        config = self.get_config("mail")

        if message is not None:
            now = datetime.now()
            mail_message = MIMEMultipart('alternative')
            mail_message['Subject'] = "%s - %s" % (now.strftime("%d/%m/%Y %H:%M"), self.subject)
            mail_message['From'] = config.get("user")
            mail_message['To'] = config.get("recipients")
            mail_message.attach(MIMEText(message, 'html'))

            try:
                server = smtplib.SMTP(config.get("server") + ":" + config.get("port"))
                server.ehlo()
                server.starttls()
                server.login(config.get("user"), config.get("password"))
                server.sendmail(config.get("user"), config.get("recipients").split(','), mail_message.as_string())
                server.close()
            except Exception:
                raise Exception("erro ao enviar email")
        else:
            raise Exception("nenhuma mensagem definida")

    def get_message(self):
        if self.query is not None:
            # execute the query
            cur = self.conn.cursor()
            cur.execute(self.query)
            colnames = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            self.conn.close()

            # create a message
            message = "<html>"
            message += "<head>"
            message += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">"
            message += "</head>"
            message += "<body>"
            message += "<table border=\"1\">"
            message += "<tr bgcolor=\"#ffff00\">"
            for colname in colnames:
                message += "<th align=\"left\">"+str(colname).upper()+"</th>"
            message += "</tr>"
            for row in rows:
                message += "<tr>"
                for val in row:
                    message += "<td align=\"left\">"+str(val).upper()+"</td>"
                message += "</tr>"
            message += "</table>"
            message += "</br><i>MENSAGEM AUTOMÁTICA.</i>"
            message += "</body>"
            message += "</html>"

            return message
        else:
            raise Exception("nenhuma query definida")

    @staticmethod
    def get_config(section):
        parser = ConfigParser()
        parser.read("config/config.ini")
        config = {}

        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                config[param[0]] = param[1]
        else:
            raise Exception("erro ao obter config '%s'" % section)

        return config
