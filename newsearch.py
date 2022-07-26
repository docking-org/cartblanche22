import sys, os, subprocess, argparse
import tempfile
import psycopg2
import io
import time
import hashlib
SQLALCHEMY_BINDS = {
        # Server Database
        # 'zinc22': 'postgresql://test:@mem2.cluster.ucsf.bkslab.org:5432/zinc22',
        # 'zinc22_common': 'postgresql://zincuser:@10.20.1.17:5534/zinc22_common',
        # 'zinc22': 'postgresql://test:@10.20.0.38:5432/zinc22',
        # 'tin': 'postgresql://tinuser:usertin@10.20.1.17:5437/tin',
        # '10.20.1.16:5434': 'postgresql://tinuser:usertin@10.20.1.16:5434/tin',
        # '10.20.1.16:5435': 'postgresql://tinuser:usertin@10.20.1.16:5435/tin',
        # '10.20.1.16:5436': 'postgresql://tinuser:usertin@10.20.1.16:5436/tin',
        # '10.20.1.16:5437': 'postgresql://tinuser:usertin@10.201.16:5438/tin',
        # '10.20.1.16:5439': 'postgresql://tinuser:usertin@10.20.1.1.1.16:5437/tin',
        # '10.20.1.16:5438': 'postgresql://tinuser:usertin@10.20.6:5439/tin',
        # '10.20.1.16:5440': 'postgresql://tinuser:usertin@10.20.1.16:5440/tin',
        # '10.20.1.16:5441': 'postgresql://tinuser:usertin@10.20.1.16:5441/tin',
        # '10.20.1.16:5442': 'postgresql://tinuser:usertin@10.20.1.16:5442/tin',
        # '10.20.1.16:5443': 'postgresql://tinuser:usertin@10.20.1.16:5443/tin',
        # '10.20.1.16:5444': 'postgresql://tinuser:usertin@10.20.1.16:5444/tin',
        # '10.20.1.16:5445': 'postgresql://tinuser:usertin@10.20.1.16:5445/tin',
        # '10.20.1.16:5446': 'postgresql://tinuser:usertin@10.20.1.16:5446/tin',
        # '10.20.1.16:5447': 'postgresql://tinuser:usertin@10.20.1.16:5447/tin',
        # '10.20.1.16:5448': 'postgresql://tinuser:usertin@10.20.1.16:5448/tin',
        # '10.20.1.16:5449': 'postgresql://tinuser:usertin@10.20.1.16:5449/tin',
        # '10.20.1.17:5434': 'postgresql://tinuser:usertin@10.20.1.17:5434/tin',
        # '10.20.1.17:5435': 'postgresql://tinuser:usertin@10.20.1.17:5435/tin',
        # '10.20.1.17:5436': 'postgresql://tinuser:usertin@10.20.1.17:5436/tin',
        # '10.20.1.17:5437': 'postgresql://tinuser:usertin@10.20.1.17:5437/tin',
        # '10.20.1.17:5438': 'postgresql://tinuser:usertin@10.20.1.17:5438/tin',
        # '10.20.1.17:5439': 'postgresql://tinuser:usertin@10.20.1.17:5439/tin',
        # '10.20.1.17:5440': 'postgresql://tinuser:usertin@10.20.1.17:5440/tin',
        # '10.20.1.17:5441': 'postgresql://tinuser:usertin@10.20.1.17:5441/tin',
        # '10.20.1.17:5442': 'postgresql://tinuser:usertin@10.20.1.17:5442/tin',
        # '10.20.1.17:5443': 'postgresql://tinuser:usertin@10.20.1.17:5443/tin',
        # '10.20.1.17:5444': 'postgresql://tinuser:usertin@10.20.1.17:5444/tin',
        # '10.20.1.17:5446': 'postgresql://tinuser:usertin@10.20.1.17:5446/tin',
        # '10.20.1.18:5434': 'postgresql://tinuser:usertin@10.20.1.18:5434/tin',
        # '10.20.1.18:5435': 'postgresql://tinuser:usertin@10.20.1.18:5435/tin',
        # '10.20.1.18:5436': 'postgresql://tinuser:usertin@10.20.1.18:5436/tin',
        # '10.20.1.18:5437': 'postgresql://tinuser:usertin@10.20.1.18:5437/tin',
        # '10.20.1.18:5438': 'postgresql://tinuser:usertin@10.20.1.18:5438/tin',
        # '10.20.1.18:5439': 'postgresql://tinuser:usertin@10.20.1.18:5439/tin',
        # '10.20.1.18:5440': 'postgresql://tinuser:usertin@10.20.1.18:5440/tin',
        # '10.20.1.18:5441': 'postgresql://tinuser:usertin@10.20.1.18:5441/tin',
        # '10.20.1.18:5442': 'postgresql://tinuser:usertin@10.20.1.18:5442/tin',
        # '10.20.1.18:5443': 'postgresql://tinuser:usertin@10.20.1.18:5443/tin',
        # '10.20.1.18:5444': 'postgresql://tinuser:usertin@10.20.1.18:5444/tin',
        # '10.20.1.18:5445': 'postgresql://tinuser:usertin@10.20.1.18:5445/tin',
        # '10.20.1.18:5446': 'postgresql://tinuser:usertin@10.20.1.18:5446/tin',
        # '10.20.1.18:5447': 'postgresql://tinuser:usertin@10.20.1.18:5447/tin',
        # '10.20.1.18:5448': 'postgresql://tinuser:usertin@10.20.1.18:5448/tin',
        # '10.20.1.18:5449': 'postgresql://tinuser:usertin@10.20.1.18:5449/tin',
        # '10.20.1.18:5450': 'postgresql://tinuser:usertin@10.20.1.18:5450/tin',
        # '10.20.1.18:5451': 'postgresql://tinuser:usertin@10.20.1.18:5451/tin',
        # '10.20.1.18:5452': 'postgresql://tinuser:usertin@10.20.1.18:5452/tin',
        # '10.20.1.19:5434': 'postgresql://tinuser:usertin@10.20.1.19:5434/tin',
        # '10.20.1.19:5435': 'postgresql://tinuser:usertin@10.20.1.19:5435/tin',
        # '10.20.1.19:5436': 'postgresql://tinuser:usertin@10.20.1.19:5436/tin',
        # '10.20.1.19:5437': 'postgresql://tinuser:usertin@10.20.1.19:5437/tin',
        # '10.20.1.19:5438': 'postgresql://tinuser:usertin@10.20.1.19:5438/tin',
        # '10.20.1.19:5439': 'postgresql://tinuser:usertin@10.20.1.19:5439/tin',
        # '10.20.1.19:5440': 'postgresql://tinuser:usertin@10.20.1.19:5440/tin',
        # '10.20.1.19:5441': 'postgresql://tinuser:usertin@10.20.1.19:5441/tin',
        # '10.20.1.19:5442': 'postgresql://tinuser:usertin@10.20.1.19:5442/tin',
        # '10.20.1.19:5443': 'postgresql://tinuser:usertin@10.20.1.19:5443/tin',
        # '10.20.1.19:5444': 'postgresql://tinuser:usertin@10.20.1.19:5444/tin',
        # '10.20.1.19:5445': 'postgresql://tinuser:usertin@10.20.1.19:5445/tin',
        # '10.20.1.19:5446': 'postgresql://tinuser:usertin@10.20.1.19:5446/tin',
        # '10.20.1.19:5447': 'postgresql://tinuser:usertin@10.20.1.19:5447/tin',
        # '10.20.1.19:5448': 'postgresql://tinuser:usertin@10.20.1.19:5448/tin',
        # '10.20.1.20:5434': 'postgresql://tinuser:usertin@10.20.1.20:5434/tin',
        # '10.20.1.20:5435': 'postgresql://tinuser:usertin@10.20.1.20:5435/tin',
        # '10.20.1.20:5436': 'postgresql://tinuser:usertin@10.20.1.20:5436/tin',
        # '10.20.1.20:5437': 'postgresql://tinuser:usertin@10.20.1.20:5437/tin',
        # '10.20.1.20:5438': 'postgresql://tinuser:usertin@10.20.1.20:5438/tin',
        # '10.20.1.20:5439': 'postgresql://tinuser:usertin@10.20.1.20:5439/tin',
        # '10.20.1.20:5440': 'postgresql://tinuser:usertin@10.20.1.20:5440/tin',
        # '10.20.1.20:5441': 'postgresql://tinuser:usertin@10.20.1.20:5441/tin',
        # '10.20.1.20:5442': 'postgresql://tinuser:usertin@10.20.1.20:5442/tin',
        # '10.20.1.20:5443': 'postgresql://tinuser:usertin@10.20.1.20:5443/tin',
        # '10.20.1.20:5444': 'postgresql://tinuser:usertin@10.20.1.20:5444/tin',
        # '10.20.1.20:5445': 'postgresql://tinuser:usertin@10.20.1.20:5445/tin',
        # '10.20.1.20:5446': 'postgresql://tinuser:usertin@10.20.1.20:5446/tin',
        # '10.20.1.20:5447': 'postgresql://tinuser:usertin@10.20.1.20:5447/tin',
        # '10.20.1.20:5448': 'postgresql://tinuser:usertin@10.20.1.20:5448/tin',
        # '10.20.1.20:5449': 'postgresql://tinuser:usertin@10.20.1.20:5449/tin',
        # '10.20.5.34:5434': 'postgresql://tinuser:usertin@10.20.5.34:5434/tin',
        # '10.20.5.34:5435': 'postgresql://tinuser:usertin@10.20.5.34:5435/tin',
        # '10.20.5.34:5436': 'postgresql://tinuser:usertin@10.20.5.34:5436/tin',
        # '10.20.5.34:5437': 'postgresql://tinuser:usertin@10.20.5.34:5437/tin',
        # '10.20.5.34:5438': 'postgresql://tinuser:usertin@10.20.5.34:5438/tin',
        # '10.20.5.34:5439': 'postgresql://tinuser:usertin@10.20.5.34:5439/tin',
        # '10.20.5.34:5440': 'postgresql://tinuser:usertin@10.20.5.34:5440/tin',
        # '10.20.5.34:5441': 'postgresql://tinuser:usertin@10.20.5.34:5441/tin',
        # '10.20.5.34:5442': 'postgresql://tinuser:usertin@10.20.5.34:5442/tin',
        # '10.20.5.34:5443': 'postgresql://tinuser:usertin@10.20.5.34:5443/tin',
        # '10.20.5.34:5444': 'postgresql://tinuser:usertin@10.20.5.34:5444/tin',
        # '10.20.5.34:5445': 'postgresql://tinuser:usertin@10.20.5.34:5445/tin',
        # '10.20.5.34:5446': 'postgresql://tinuser:usertin@10.20.5.34:5446/tin',
        # '10.20.5.34:5447': 'postgresql://tinuser:usertin@10.20.5.34:5447/tin',
        # '10.20.5.34:5448': 'postgresql://tinuser:usertin@10.20.5.34:5448/tin',
        # '10.20.5.34:5449': 'postgresql://tinuser:usertin@10.20.5.34:5449/tin',
        # '10.20.5.34:5450': 'postgresql://tinuser:usertin@10.20.5.34:5450/tin',
        # '10.20.5.34:5451': 'postgresql://tinuser:usertin@10.20.5.34:5451/tin',
        # '10.20.5.35:5434': 'postgresql://tinuser:usertin@10.20.5.35:5434/tin',
        # '10.20.5.35:5435': 'postgresql://tinuser:usertin@10.20.5.35:5435/tin',
        # '10.20.5.35:5436': 'postgresql://tinuser:usertin@10.20.5.35:5436/tin',
        # '10.20.5.35:5437': 'postgresql://tinuser:usertin@10.20.5.35:5437/tin',
        # '10.20.5.35:5438': 'postgresql://tinuser:usertin@10.20.5.35:5438/tin',
        # '10.20.5.35:5439': 'postgresql://tinuser:usertin@10.20.5.35:5439/tin',
        # '10.20.5.35:5440': 'postgresql://tinuser:usertin@10.20.5.35:5440/tin',
        # '10.20.5.35:5441': 'postgresql://tinuser:usertin@10.20.5.35:5441/tin',
        # '10.20.5.35:5442': 'postgresql://tinuser:usertin@10.20.5.35:5442/tin',
        # '10.20.5.35:5443': 'postgresql://tinuser:usertin@10.20.5.35:5443/tin',
        # '10.20.5.35:5444': 'postgresql://tinuser:usertin@10.20.5.35:5444/tin',
        # '10.20.5.35:5445': 'postgresql://tinuser:usertin@10.20.5.35:5445/tin',
        # '10.20.5.35:5446': 'postgresql://tinuser:usertin@10.20.5.35:5446/tin',
        # '10.20.5.35:5447': 'postgresql://tinuser:usertin@10.20.5.35:5447/tin',
        # '10.20.5.35:5448': 'postgresql://tinuser:usertin@10.20.5.35:5448/tin',
        # '10.20.5.35:5449': 'postgresql://tinuser:usertin@10.20.5.35:5449/tin',
        # '10.20.5.35:5450': 'postgresql://tinuser:usertin@10.20.5.35:5450/tin',
        # '10.20.5.35:5451': 'postgresql://tinuser:usertin@10.20.5.35:5451/tin',
        # '10.20.5.35:5452': 'postgresql://tinuser:usertin@10.20.5.35:5452/tin',
        # '10.20.9.19:5434': 'postgresql://tinuser:usertin@10.20.9.19:5434/tin',
        # '10.20.9.19:5435': 'postgresql://tinuser:usertin@10.20.9.19:5435/tin',
        # '10.20.9.19:5436': 'postgresql://tinuser:usertin@10.20.9.19:5436/tin',
        # '10.20.9.19:5437': 'postgresql://tinuser:usertin@10.20.9.19:5437/tin',
        # '10.20.9.19:5438': 'postgresql://tinuser:usertin@10.20.9.19:5438/tin',
        # '10.20.9.19:5439': 'postgresql://tinuser:usertin@10.20.9.19:5439/tin',
        # '10.20.9.19:5440': 'postgresql://tinuser:usertin@10.20.9.19:5440/tin',
        # '10.20.9.19:5441': 'postgresql://tinuser:usertin@10.20.9.19:5441/tin',
        # '10.20.9.19:5442': 'postgresql://tinuser:usertin@10.20.9.19:5442/tin',
        # '10.20.9.19:5443': 'postgresql://tinuser:usertin@10.20.9.19:5443/tin',
        # '10.20.9.19:5444': 'postgresql://tinuser:usertin@10.20.9.19:5444/tin',
        # '10.20.9.20:5434': 'postgresql://tinuser:usertin@10.20.9.20:5434/tin',
        # '10.20.9.20:5435': 'postgresql://tinuser:usertin@10.20.9.20:5435/tin',
        # '10.20.9.20:5436': 'postgresql://tinuser:usertin@10.20.9.20:5436/tin',
        # '10.20.9.20:5437': 'postgresql://tinuser:usertin@10.20.9.20:5437/tin',
        # '10.20.9.20:5438': 'postgresql://tinuser:usertin@10.20.9.20:5438/tin',
        # '10.20.9.20:5439': 'postgresql://tinuser:usertin@10.20.9.20:5439/tin',
        # '10.20.9.20:5440': 'postgresql://tinuser:usertin@10.20.9.20:5440/tin',
        # '10.20.9.20:5441': 'postgresql://tinuser:usertin@10.20.9.20:5441/tin',
        # '10.20.9.20:5442': 'postgresql://tinuser:usertin@10.20.9.20:5442/tin',
        # '10.20.9.20:5443': 'postgresql://tinuser:usertin@10.20.9.20:5443/tin',
        # '10.20.9.20:5444': 'postgresql://tinuser:usertin@10.20.9.20:5444/tin',
        # '10.20.1.21:5434': 'postgresql://tinuser:usertin@10.20.1.21:5434/tin',
        # '10.20.1.21:5435': 'postgresql://tinuser:usertin@10.20.1.21:5435/tin',
        # '10.20.1.21:5436': 'postgresql://tinuser:usertin@10.20.1.21:5436/tin',
        # '10.20.1.21:5437': 'postgresql://tinuser:usertin@10.20.1.21:5437/tin',
        # '10.20.1.21:5438': 'postgresql://tinuser:usertin@10.20.1.21:5438/tin',
        # '10.20.1.21:5439': 'postgresql://tinuser:usertin@10.20.1.21:5439/tin',
        # '10.20.1.21:5440': 'postgresql://tinuser:usertin@10.20.1.21:5440/tin',
        # '10.20.1.21:5441': 'postgresql://tinuser:usertin@10.20.1.21:5441/tin',
        # '10.20.1.21:5442': 'postgresql://tinuser:usertin@10.20.1.21:5442/tin',
        # '10.20.1.21:5443': 'postgresql://tinuser:usertin@10.20.1.21:5443/tin',
        # '10.20.1.21:5444': 'postgresql://tinuser:usertin@10.20.1.21:5444/tin',
        # '10.20.1.21:5445': 'postgresql://tinuser:usertin@10.20.1.21:5445/tin',
        # '10.20.1.21:5446': 'postgresql://tinuser:usertin@10.20.1.21:5446/tin',
        
        # Local Database
        'zinc22_common': 'postgresql://zincuser:@localhost:5584/zinc22_common',
        'zinc22': 'postgresql://test@localhost:2223/zinc22',
        'tin': 'postgresql://tinuser:usertin@localhost:5437/tin',
        "10.20.1.16:5434": "postgresql://tinuser:usertin@localhost:5434/tin",
        "10.20.1.16:5435": "postgresql://tinuser:usertin@localhost:5435/tin",
        "10.20.1.16:5436": "postgresql://tinuser:usertin@localhost:5436/tin",
        "10.20.1.16:5437": "postgresql://tinuser:usertin@localhost:5437/tin",
        "10.20.1.16:5438": "postgresql://tinuser:usertin@localhost:5438/tin",
        "10.20.1.16:5439": "postgresql://tinuser:usertin@localhost:5439/tin",
        "10.20.1.16:5440": "postgresql://tinuser:usertin@localhost:5440/tin",
        "10.20.1.16:5441": "postgresql://tinuser:usertin@localhost:5441/tin",
        "10.20.1.16:5442": "postgresql://tinuser:usertin@localhost:5442/tin",
        "10.20.1.16:5443": "postgresql://tinuser:usertin@localhost:5443/tin",
        "10.20.1.16:5444": "postgresql://tinuser:usertin@localhost:5444/tin",
        "10.20.1.16:5445": "postgresql://tinuser:usertin@localhost:5445/tin",
        "10.20.1.16:5446": "postgresql://tinuser:usertin@localhost:5446/tin",
        "10.20.1.16:5447": "postgresql://tinuser:usertin@localhost:5447/tin",
        "10.20.1.16:5448": "postgresql://tinuser:usertin@localhost:5448/tin",
        "10.20.1.16:5449": "postgresql://tinuser:usertin@localhost:5449/tin",
        "10.20.1.17:5434": "postgresql://tinuser:usertin@localhost:5450/tin",
        "10.20.1.17:5435": "postgresql://tinuser:usertin@localhost:5451/tin",
        "10.20.1.17:5436": "postgresql://tinuser:usertin@localhost:5452/tin",
        "10.20.1.17:5437": "postgresql://tinuser:usertin@localhost:5453/tin",
        "10.20.1.17:5438": "postgresql://tinuser:usertin@localhost:5454/tin",
        "10.20.1.17:5439": "postgresql://tinuser:userti*@localhost:5456/tin",
        "10.20.1.17:5441": "postgresql://tinuser:usertin@localhost:5457/tin",
        "10.20.1.17:5442": "postgresql://tinuser:usertin@localhost:5458/tin",
        "10.20.1.17:5443": "postgresql://tinuser:usertin@localhost:5459/tin",
        "10.20.1.17:5444": "postgresql://tinuser:usertin@localhost:5460/tin",
        "10.20.1.17:5446": "postgresql://tinuser:usertin@localhost:5461/tin",
        "10.20.1.18:5434": "postgresql://tinuser:usertin@localhost:5462/tin",
        "10.20.1.18:5435": "postgresql://tinuser:usertin@localhost:5463/tin",
        "10.20.1.18:5436": "postgresql://tinuser:usertin@localhost:5464/tin",
        "10.20.1.18:5437": "postgresql://tinuser:usertin@localhost:5465/tin",
        "10.20.1.18:5438": "postgresql://tinuser:usertin@localhost:5466/tin",
        "10.20.1.18:5439": "postgresql://tinuser:usertin@localhost:5467/tin",
        "10.20.1.18:5440": "postgresql://tinuser:usertin@localhost:5468/tin",
        "10.20.1.18:5441": "postgresql://tinuser:usertin@localhost:5469/tin",
        "10.20.1.18:5442": "postgresql://tinuser:usertin@localhost:5470/tin",
        "10.20.1.18:5443": "postgresql://tinuser:usertin@localhost:5471/tin",
        "10.20.1.18:5444": "postgresql://tinuser:usertin@localhost:5472/tin",
        "10.20.1.18:5445": "postgresql://tinuser:usertin@localhost:5473/tin",
        "10.20.1.18:5446": "postgresql://tinuser:usertin@localhost:5474/tin",
        "10.20.1.18:5447": "postgresql://tinuser:usertin@localhost:5475/tin",
        "10.20.1.18:5448": "postgresql://tinuser:usertin@localhost:5476/tin",
        "10.20.1.18:5449": "postgresql://tinuser:usertin@localhost:5477/tin",
        "10.20.1.18:5450": "postgresql://tinuser:usertin@localhost:5478/tin",
        "10.20.1.18:5451": "postgresql://tinuser:usertin@localhost:5479/tin",
        "10.20.1.18:5452": "postgresql://tinuser:usertin@localhost:5480/tin",
        "10.20.1.19:5434": "postgresql://tinuser:usertin@localhost:5481/tin",
        "10.20.1.19:5435": "postgresql://tinuser:usertin@localhost:5482/tin",
        "10.20.1.19:5436": "postgresql://tinuser:usertin@localhost:5483/tin",
        "10.20.1.19:5437": "postgresql://tinuser:usertin@localhost:5484/tin",
        "10.20.1.19:5438": "postgresql://tinuser:usertin@localhost:5485/tin",
        "10.20.1.19:5439": "postgresql://tinuser:usertin@localhost:5486/tin",
        "10.20.1.19:5440": "postgresql://tinuser:usertin@localhost:5487/tin",
        "10.20.1.19:5441": "postgresql://tinuser:usertin@localhost:5488/tin",
        "10.20.1.19:5442": "postgresql://tinuser:usertin@localhost:5489/tin",
        "10.20.1.19:5443": "postgresql://tinuser:usertin@localhost:5490/tin",
        "10.20.1.19:5444": "postgresql://tinuser:usertin@localhost:5491/tin",
        "10.20.1.19:5445": "postgresql://tinuser:usertin@localhost:5492/tin",
        "10.20.1.19:5446": "postgresql://tinuser:usertin@localhost:5493/tin",
        "10.20.1.19:5447": "postgresql://tinuser:usertin@localhost:5494/tin",
        "10.20.1.19:5448": "postgresql://tinuser:usertin@localhost:5495/tin",
        "10.20.1.20:5434": "postgresql://tinuser:usertin@localhost:5496/tin",
        "10.20.1.20:5435": "postgresql://tinuser:usertin@localhost:5497/tin",
        "10.20.1.20:5436": "postgresql://tinuser:usertin@localhost:5498/tin",
        "10.20.1.20:5437": "postgresql://tinuser:usertin@localhost:5499/tin",
        "10.20.1.20:5438": "postgresql://tinuser:usertin@localhost:5500/tin",
        "10.20.1.20:5439": "postgresql://tinuser:usertin@localhost:5501/tin",
        "10.20.1.20:5440": "postgresql://tinuser:usertin@localhost:5502/tin",
        "10.20.1.20:5441": "postgresql://tinuser:usertin@localhost:5503/tin",
        "10.20.1.20:5442": "postgresql://tinuser:usertin@localhost:5504/tin",
        "10.20.1.20:5443": "postgresql://tinuser:usertin@localhost:5505/tin",
        "10.20.1.20:5444": "postgresql://tinuser:usertin@localhost:5506/tin",
        "10.20.1.20:5445": "postgresql://tinuser:usertin@localhost:5507/tin",
        "10.20.1.20:5446": "postgresql://tinuser:usertin@localhost:5508/tin",
        "10.20.1.20:5447": "postgresql://tinuser:usertin@localhost:5509/tin",
        "10.20.1.20:5448": "postgresql://tinuser:usertin@localhost:5510/tin",
        "10.20.1.20:5449": "postgresql://tinuser:usertin@localhost:5511/tin",
        "10.20.5.34:5434": "postgresql://tinuser:usertin@localhost:5512/tin",
        "10.20.5.34:5435": "postgresql://tinuser:usertin@localhost:5513/tin",
        "10.20.5.34:5436": "postgresql://tinuser:usertin@localhost:5514/tin",
        "10.20.5.34:5437": "postgresql://tinuser:usertin@localhost:5515/tin",
        "10.20.5.34:5438": "postgresql://tinuser:usertin@localhost:5516/tin",
        "10.20.5.34:5439": "postgresql://tinuser:usertin@localhost:5517/tin",
        "10.20.5.34:5440": "postgresql://tinuser:usertin@localhost:5518/tin",
        "10.20.5.34:5441": "postgresql://tinuser:usertin@localhost:5519/tin",
        "10.20.5.34:5442": "postgresql://tinuser:usertin@localhost:5520/tin",
        "10.20.5.34:5443": "postgresql://tinuser:usertin@localhost:5521/tin",
        "10.20.5.34:5444": "postgresql://tinuser:usertin@localhost:5522/tin",
        "10.20.5.34:5445": "postgresql://tinuser:usertin@localhost:5523/tin",
        "10.20.5.34:5446": "postgresql://tinuser:usertin@localhost:5524/tin",
        "10.20.5.34:5447": "postgresql://tinuser:usertin@localhost:5525/tin",
        "10.20.5.34:5448": "postgresql://tinuser:usertin@localhost:5526/tin",
        "10.20.5.34:5449": "postgresql://tinuser:usertin@localhost:5527/tin",
        "10.20.5.34:5450": "postgresql://tinuser:usertin@localhost:5528/tin",
        "10.20.5.34:5451": "postgresql://tinuser:usertin@localhost:5529/tin",
        "10.20.5.35:5434": "postgresql://tinuser:usertin@localhost:5530/tin",
        "10.20.5.35:5435": "postgresql://tinuser:usertin@localhost:5531/tin",
        "10.20.5.35:5436": "postgresql://tinuser:usertin@localhost:5532/tin",
        "10.20.5.35:5437": "postgresql://tinuser:usertin@localhost:5533/tin",
        "10.20.5.35:5438": "postgresql://tinuser:usertin@localhost:5534/tin",
        "10.20.5.35:5439": "postgresql://tinuser:usertin@localhost:5535/tin",
        "10.20.5.35:5440": "postgresql://tinuser:usertin@localhost:5536/tin",
        "10.20.5.35:5441": "postgresql://tinuser:usertin@localhost:5537/tin",
        "10.20.5.35:5442": "postgresql://tinuser:usertin@localhost:5538/tin",
        "10.20.5.35:5443": "postgresql://tinuser:usertin@localhost:5539/tin",
        "10.20.5.35:5444": "postgresql://tinuser:usertin@localhost:5540/tin",
        "10.20.5.35:5445": "postgresql://tinuser:usertin@localhost:5541/tin",
        "10.20.5.35:5446": "postgresql://tinuser:usertin@localhost:5542/tin",
        "10.20.5.35:5447": "postgresql://tinuser:usertin@localhost:5543/tin",
        "10.20.5.35:5448": "postgresql://tinuser:usertin@localhost:5544/tin",
        "10.20.5.35:5449": "postgresql://tinuser:usertin@localhost:5545/tin",
        "10.20.5.35:5450": "postgresql://tinuser:usertin@localhost:5546/tin",
        "10.20.5.35:5451": "postgresql://tinuser:usertin@localhost:5547/tin",
        "10.20.5.35:5452": "postgresql://tinuser:usertin@localhost:5548/tin",
        "10.20.9.19:5434": "postgresql://tinuser:usertin@localhost:5549/tin",
        "10.20.9.19:5435": "postgresql://tinuser:usertin@localhost:5550/tin",
        "10.20.9.19:5436": "postgresql://tinuser:usertin@localhost:5551/tin",
        "10.20.9.19:5437": "postgresql://tinuser:usertin@localhost:5552/tin",
        "10.20.9.19:5438": "postgresql://tinuser:usertin@localhost:5553/tin",
        "10.20.9.19:5439": "postgresql://tinuser:usertin@localhost:5554/tin",
        "10.20.9.19:5440": "postgresql://tinuser:usertin@localhost:5555/tin",
        "10.20.9.19:5441": "postgresql://tinuser:usertin@localhost:5556/tin",
        "10.20.9.19:5442": "postgresql://tinuser:usertin@localhost:5557/tin",
        "10.20.9.19:5443": "postgresql://tinuser:usertin@localhost:5558/tin",
        "10.20.9.19:5444": "postgresql://tinuser:usertin@localhost:5559/tin",
        "10.20.9.20:5434": "postgresql://tinuser:usertin@localhost:5560/tin",
        "10.20.9.20:5435": "postgresql://tinuser:usertin@localhost:5561/tin",
        "10.20.9.20:5436": "postgresql://tinuser:usertin@localhost:5562/tin",
        "10.20.9.20:5437": "postgresql://tinuser:usertin@localhost:5563/tin",
        "10.20.9.20:5438": "postgresql://tinuser:usertin@localhost:5564/tin",
        "10.20.9.20:5439": "postgresql://tinuser:usertin@localhost:5565/tin",
        "10.20.9.20:5440": "postgresql://tinuser:usertin@localhost:5566/tin",
        "10.20.9.20:5441": "postgresql://tinuser:usertin@localhost:5567/tin",
        "10.20.9.20:5442": "postgresql://tinuser:usertin@localhost:5568/tin",
        "10.20.9.20:5443": "postgresql://tinuser:usertin@localhost:5569/tin",
        "10.20.9.20:5444": "postgresql://tinuser:usertin@localhost:5570/tin",
        "10.20.1.21:5434": "postgresql://tinuser:usertin@localhost:5571/tin",
        "10.20.1.21:5435": "postgresql://tinuser:usertin@localhost:5572/tin",
        "10.20.1.21:5436": "postgresql://tinuser:usertin@localhost:5573/tin",
        "10.20.1.21:5437": "postgresql://tinuser:usertin@localhost:5574/tin",
        "10.20.1.21:5438": "postgresql://tinuser:usertin@localhost:5575/tin",
        "10.20.1.21:5439": "postgresql://tinuser:usertin@localhost:5576/tin",
        "10.20.1.21:5440": "postgresql://tinuser:usertin@localhost:5577/tin",
        "10.20.1.21:5441": "postgresql://tinuser:usertin@localhost:5578/tin",
        "10.20.1.21:5442": "postgresql://tinuser:usertin@localhost:5579/tin",
        "10.20.1.21:5443": "postgresql://tinuser:usertin@localhost:5580/tin",
        "10.20.1.21:5444": "postgresql://tinuser:usertin@localhost:5581/tin",
        "10.20.1.21:5445": "postgresql://tinuser:usertin@localhost:5582/tin",
        "10.20.1.21:5446": "postgresql://tinuser:usertin@localhost:5583/tin",
    }

# all stuff related to parsing zinc ids goes here
digits="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
logp_range="M500 M400 M300 M200 M100 M000 P000 P010 P020 P030 P040 P050 P060 P070 P080 P090 P100 P110 P120 P130 P140 P150 P160 P170 P180 P190 P200 P210 P220 P230 P240 P250 P260 P270 P280 P290 P300 P310 P320 P330 P340 P350 P360 P370 P380 P390 P400 P410 P420 P430 P440 P450 P460 P470 P480 P490 P500 P600 P700 P800 P900".split(" ")
#logp_range_rev={e:i for i, e in enumerate(logp_range)}
digits_map = { digit : i for i, digit in enumerate(digits) }
b62_table = [62**i for i in range(12)]
def base62_rev(s):
    tot = 0
    for i, c in enumerate(reversed(s)):
        val = digits_map[c]
        tot += val * b62_table[i]
    return tot
def base62(n):
    b62_str=""
    while n >= 62:
        n, r = divmod(n, 62)
        b62_str += digits[r]
    b62_str += digits[n]
    return ''.join(reversed(b62_str))

def get_tranche(zinc_id):
    hac = base62_rev(zinc_id[4])
    lgp = base62_rev(zinc_id[5])
    tranche = "H{:>02d}{}".format(hac, logp_range[lgp])
    return tranche

def get_tin_partition(zinc_id, tranche_map):
    return tranche_map.get(get_tranche(zinc_id)) or "fake"
    
def get_tin_partition_by_id(machine_id, machine_id_map):
    return machine_id_map.get(machine_id) or "fake"

def get_conn_string(partition_host_port, db='tin', user='tinuser'):
    host, port = partition_host_port.split(':')
    if host == os.uname()[1].split('.')[0]:
        host = "localhost"
    host = host.split('-')
    toNum  = "10.20."+ host[1]+"."+host[2]
    return SQLALCHEMY_BINDS[toNum+":"+port]
    #return "postgresql://{0}@{1}:{2}/{3}".format(user, host, port, db)

def get_sub_id(zinc_id):
    return base62_rev(zinc_id[8:])

def get_zinc_id(sub_id, tranche_name):
    if not tranche_name:
        return "ZINC" + "??00" + "{:0>8s}".format(base62(sub_id))
    hac = digits[int(tranche_name[1:3])]
    lgp = digits[logp_range.index(tranche_name[3:])]
    zid = "ZINC" + hac + lgp + "00" + "{:0>8s}".format(base62(sub_id))
    return zid

# shameless steal from stackoverflow https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters?noredirect=1&lq=1
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = 'X', printEnd = "\n", t_elapsed=0, projected=0):
    percent = 100 * (iteration / float(total))
    filledLength_current = int(length * iteration // total)
    filledLength_project = int(length * (iteration+projected) // total) # i added this bit
    bar = fill * filledLength_current + '/' * (filledLength_project-filledLength_current) + '-' * (length - filledLength_project)
    t_elapsed_str = "{:>7.2f}s".format(t_elapsed)
    print(f'\r{prefix} |{bar}| {percent:> 7.2f}% {t_elapsed_str} {iteration:>12}/{total:<12} {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total and printEnd != '\n':
        print()
        
def parse_tin_results(search_curs, output_file, tranches_internal):
    tranches_internal_rev = { t[1] : t[0] for t in tranches_internal.items() }
    results = search_curs.fetchmany(5000)
    while len(results) > 0:
        for result in results:
            smiles          = result[0] or "_null_"
            sub_id          = result[1]
            tranche_id_orig = result[2]
            others          = [str(r) or "_null_" for r in result[3:]]
            tranche_name    = tranches_internal_rev[tranche_id_orig]
            zinc_id = get_zinc_id(sub_id, tranche_name)
            output_file.write('\t'.join([smiles, zinc_id, tranche_name] + others) + '\n')
        results = search_curs.fetchmany(5000)
        
def parse_tin_results_cat_id(search_curs, output_file):
    results = search_curs.fetchmany(5000)
    while len(results) > 0:
        for result in results:
            smiles          = result[0] or "_null_"
            sub_id          = result[1]
            tranche_name    = result[2]
            supplier_code   = result[3]
            catalog         = result[4] or "_null_"
            if sub_id:
                zinc_id = get_zinc_id(sub_id, tranche_name)
            else:
                zinc_id = "_null_"
            output_file.write('\t'.join([smiles, zinc_id, tranche_name, supplier_code, catalog]) + '\n')
        results = search_curs.fetchmany(5000)

def get_vendor_results_antimony(data_file, search_curs, output_file, missing_file):
    search_curs.execute("create temporary table tq_in (supplier_code text)")
    search_curs.copy_from(data_file, 'tq_in', columns=['supplier_code'])
    # we have a more standard query for antimony, since it's not as complicated as tin and therefore doesn't need custom database functions
    search_curs.execute("select tq_in.supplier_code, cat_content_id, machine_id_fk from tq_in left join supplier_codes on tq_in.supplier_code = supplier_codes.supplier_code left join supplier_map on sup_id = sup_id_fk")
    
    results = search_curs.fetchmany(5000)
    while len(results) > 0:
        for result in results:
            supplier_code   = result[0]
            cat_content_id  = result[1]
            machine_id_fk   = result[2]
            if not cat_content_id:
                # we need to pass data returned by antimony to tin
                # it doesn't make sense to look up a bunch of nulls, so save the misses from this stage separately and add them to the end result later
                missing_file.write('\t'.join(["_null_", "_null_", "_null_", supplier_code, "_null_"]) + '\n')
            else:
                output_file.write('\t'.join([supplier_code, str(cat_content_id), str(machine_id_fk)]) + '\n')
        results = search_curs.fetchmany(5000)
        
def get_vendor_results_cat_id(data_file, search_curs, output_file):
    search_curs.execute("create temporary table cb_vendor_input (supplier_code text)")
    search_curs.copy_from(data_file, 'cb_vendor_input', sep=',', columns=['supplier_code'])
    search_curs.execute("create temporary table cb_pairs_output (smiles text, sub_id bigint, tranche_id smallint, supplier_code text, cat_content_id bigint, cat_id smallint)")
    search_curs.execute("call cb_get_some_pairs_by_vendor()")
    search_curs.execute("select smiles, sub_id, tranches.tranche_name, supplier_code, catalog.short_name from cb_pairs_output left join tranches on cb_pairs_output.tranche_id = tranches.tranche_id left join catalog on cb_pairs_output.cat_id = catalog.cat_id")
    
    parse_tin_results_cat_id(search_curs, output_file)

def get_vendor_results(data_file, search_curs, output_file, tranches_internal):
    search_curs.execute("create temporary table cb_sub_id_input (sub_id bigint, tranche_id_orig smallint)")
    search_curs.copy_from(data_file, 'cb_sub_id_input', sep='\t', columns=['sub_id', 'tranche_id_orig'])
    search_curs.execute("create temporary table cb_pairs_output (smiles text, sub_id bigint, tranche_id smallint, supplier_code text, cat_content_id bigint, cat_id_fk smallint, tranche_id_orig smallint)")
    search_curs.execute("call cb_get_some_pairs_by_sub_id()")
    search_curs.execute("select smiles, sub_id, tranche_id_orig, supplier_code, catalog.short_name from cb_pairs_output left join catalog on cb_pairs_output.cat_id_fk = catalog.cat_id")

    parse_tin_results(search_curs, output_file, tranches_internal)

def get_smiles_results(data_file, search_curs, output_file, tranches_internal):
    search_curs.execute("create temporary table cb_sub_id_input (sub_id bigint, tranche_id_orig smallint)")
    search_curs.copy_from(data_file, 'cb_sub_id_input', sep='\t', columns=['sub_id', 'tranche_id_orig'])
    search_curs.execute("create temporary table cb_sub_output (smiles text, sub_id bigint, tranche_id smallint, tranche_id_orig smallint)")
    search_curs.execute("call get_some_substances_by_id('cb_sub_id_input', 'cb_sub_output')")
    search_curs.execute("select smiles, sub_id, tranche_id_orig from cb_sub_output")

    parse_tin_results(search_curs, output_file, tranches_internal)
   
# to do: figure out how to bring down the linecount of these functions
# a lot of logic repeated in slightly different ways between this and zinc_id_search
def vendor_search(args, client_configuration):

    t_start = time.time()

    # all configuration prepartion
    config_conn = psycopg2.connect(args.configuration_server_url)
    config_curs = config_conn.cursor()
    config_curs.execute("select tranche, host, port from tranche_mappings")
    tranche_map = {}
    for result in config_curs.fetchall():
        tranche = result[0]
        host = result[1]
        port = result[2]
        tranche_map[tranche] = ':'.join([host, str(port)])
    config_curs.execute("select machine_id, hostname, port from tin_machines")
    # extra configuration for cartblanche, translates machine_id to host:port
    machine_id_map = {}
    for result in config_curs.fetchall():
        machine_id = result[0]
        host = result[1]
        port = result[2]
        machine_id_map[machine_id] = ':'.join([host, str(port)])
    sb_partition_map = {}
    config_curs.execute("select hashseq, host, port from antimony_hash_partitions ahp left join antimony_machines am on ahp.partition = am.partition")
    for result in config_curs.fetchall():
        hashseq = result[0]
        host    = result[1]
        port    = result[2]
        sb_partition_map[hashseq] = ':'.join([host, str(port)])
        
    input_size = os.stat(args.input_file)
    
    input_size = os.stat(args.input_file)
    expected_result_size = input_size.st_size * 2.5
    if expected_result_size > client_configuration["mem_max_cached_file"]:
        data_file = tempfile.NamedTemporaryFile(mode='w+')
        tf_input  = tempfile.NamedTemporaryFile(mode='w+')
        tf_inter  = tempfile.NamedTemporaryFile(mode='w+')
    else:
        # use stringIO if the file is small enough to fit into memory
        data_file = io.StringIO()
        tf_input  = tempfile.NamedTemporaryFile(mode='w+', dir='/dev/shm') # to use gnu sort we need an actual file (or a thread writing the StringIO data concurrently, which is too complicated for my taste)
        tf_inter  = tempfile.NamedTemporaryFile(mode='w+', dir='/dev/shm')
        
    with data_file, tf_input, tf_inter, open(args.results_out, 'w') as output_file:
        def sha256(a):
            return hashlib.sha256(a.encode('utf-8')).hexdigest()
        total_length = 0
        with open(args.input_file) as vendor_in:
            for vendor in vendor_in:
                vendor = vendor.strip()
                v_partition = sha256(vendor)[-4:-2] # leftmost two digits of rightmost four digits makes up the database key
                v_db = sb_partition_map[v_partition]
                tf_input.write("{} {}\n".format(vendor, v_db))
                total_length += 1
        tf_input.flush()
        
        # ========== FIRST SORT PROC- SEARCH SB ==========
        # limit sort memory usage according to configuration, we want the client-side search process to have as low a footprint as possible, while remaining fast for typical usage
        sort_mem_arg = "{}K".format(client_configuration["mem_max_sort"]//1000)
        
        # sort by the database each id belongs to 
        with subprocess.Popen(["/usr/bin/sort", "-k2", "-S{}".format(sort_mem_arg), tf_input.name], stdout=subprocess.PIPE) as sort_proc:
            def search(p_id, data_file, output_file, missing_file, args):
                search_conn = None
                try:
                    data_file.flush()
                    data_file.seek(0)
                    search_database = get_conn_string(p_id, user='antimonyuser', db='antimony')
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    # output fmt: VENDOR CAT_CONTENT_ID MACHINE_ID
                    get_vendor_results_antimony(data_file, search_curs, output_file, missing_file)
                except psycopg2.OperationalError as e:
                    print("failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database))
                    for line in data_file:
                        vendor = line.strip()
                        tokens = ["_null_", "_null_", "_null_", vendor, "_null_"]
                        missing_file.write('\t'.join(tokens) +'\n')
                finally:
                    if search_conn: search_conn.close()
        
            p_id_prev = None
            projected_size = 0
            curr_size = 0
            for line in sort_proc.stdout:
                vendor, p_id = line.decode('utf-8').strip().split()
                if p_id != p_id_prev and p_id_prev != None:
                    t_elapsed = time.time() - t_start
                    printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
                    search(p_id_prev, data_file, tf_inter, output_file, args) # set our "missing" file as output
                    curr_size += projected_size
                    projected_size = 0
                    data_file.seek(0)
                    data_file.truncate()
                data_file.write(vendor + '\n')
                projected_size += 1
                p_id_prev = p_id
            if projected_size > 0:
                t_elapsed = time.time() - t_start
                printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
                search(p_id_prev, data_file, tf_inter, output_file, args)
                data_file.seek(0)
                data_file.truncate()
                
        t_elapsed = time.time() - t_start
        printProgressBar(total_length, total_length, prefix = "", suffix="done searching sb!", length=50, t_elapsed=t_elapsed)
        tf_inter.flush()

        # ========== SECOND SORT PROC- SEARCH SN =============
        with subprocess.Popen(["/usr/bin/sort", "-k3", "-S{}".format(sort_mem_arg), tf_inter.name], stdout=subprocess.PIPE) as sort_proc:
            def search(p_id, data_file, output_file, args):
                search_conn = None
                try:
                    data_file.flush()
                    data_file.seek(0)
                    search_database = get_conn_string(p_id)
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    t_elapsed = time.time() - t_start
                    get_vendor_results_cat_id(data_file, search_curs, output_file)
                except psycopg2.OperationalError as e:
                    print("failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database))
                    for line in data_file:
                        vendor, cat_content_id = line.strip().split()
                        tokens = ["_null_", "_null_", "_null_", vendor, "_null_"]
                        output_file.write('\t'.join(tokens) +'\n')
                finally:
                    if search_conn: search_conn.close()
                    
            p_id_prev = None
            projected_size = 0
            curr_size = 0
            for line in sort_proc.stdout:
                vendor, cat_content_id, p_id = line.decode('utf-8').strip().split()
                if p_id != p_id_prev and p_id_prev != None:
                    t_elapsed = time.time() - t_start
                    p_id_prev = machine_id_map[int(p_id_prev)] # correct from number to actual database
                    printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
                    search(p_id_prev, data_file, output_file, args)
                    data_file.seek(0)
                    data_file.truncate()
                    curr_size += projected_size
                    projected_size = 0
                data_file.write(vendor + '\n')
                projected_size += 1
                p_id_prev = p_id
            if projected_size > 0:
                p_id_prev = machine_id_map[int(p_id_prev)]
                printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
                search(p_id_prev, data_file, output_file, args)
                
        t_elapsed = time.time() - t_start
        printProgressBar(total_length, total_length, prefix = "", suffix="done searching sn!", length=50, t_elapsed=t_elapsed)
    
    
    
def zinc_id_search(args, client_configuration):
    t_start = time.time()

    # all configuration prepartion
    config_conn = psycopg2.connect(args.configuration_server_url)
    config_curs = config_conn.cursor()
    config_curs.execute("select tranche, host, port from tranche_mappings")
    tranche_map = {}
    for result in config_curs.fetchall():
        tranche = result[0]
        host = result[1]
        port = result[2]
        tranche_map[tranche] = ':'.join([host, str(port)])
    
    input_size = os.stat(args.input_file)
    expected_result_size = (input_size.st_size*8) if args.get_vendors else (input_size.st_size*4)
    if expected_result_size > client_configuration["mem_max_cached_file"]:
        data_file = tempfile.NamedTemporaryFile(mode='w+')
        tf_input  = tempfile.NamedTemporaryFile(mode='w+')
    else:
        # use stringIO if the file is small enough to fit into memory
        data_file = io.StringIO()
        tf_input  = tempfile.NamedTemporaryFile(mode='w+') # except for this, see explanation in similar section above

    with tf_input, open(args.results_out, 'w') as output_file, data_file:
        total_length = 0
        with open(args.input_file) as zinc_id_in:
            for zinc_id in zinc_id_in:
                zinc_id = zinc_id.strip()
                id_partition = get_tin_partition(zinc_id, tranche_map)
                tf_input.write("{} {}\n".format(zinc_id, id_partition))
                total_length += 1
        tf_input.flush()
        
        # limit sort memory usage according to configuration, we want the client-side search process to have as low a footprint as possible, while remaining fast for typical usage
        sort_mem_arg = "{}K".format(client_configuration["mem_max_sort"]//1000)
        
        # sort by the database each id belongs to 
        with subprocess.Popen(["/usr/bin/sort", "-k2", "-S{}".format(sort_mem_arg), tf_input.name],  stdout=subprocess.PIPE) as sort_proc:
        
            def search(p_id, data_file, output_file, tranches_internal, args):
                search_conn = None
                try:
                    data_file.flush()
                    data_file.seek(0)
                    search_database = get_conn_string(p_id)
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    t_elapsed = time.time() - t_start
                    if args.get_vendors:
                        get_vendor_results(data_file, search_curs, output_file, tranches_internal)
                    else:
                        get_smiles_results(data_file, search_curs, output_file, tranches_internal)
                except psycopg2.OperationalError as e:
                    print("failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database))
                    tranches_internal_rev = {t[1] : t[0] for t in tranches_internal.items()}
                    for line in data_file:
                        sub_id, tranche_id_int = line.split()
                        sub_id = int(sub_id)
                        tranche = tranches_internal_rev[int(tranche_id_int)]
                        tokens = ["_null_", get_zinc_id(sub_id, tranche), tranche] + (2 if args.get_vendors else 0) * ["_null_"]
                        output_file.write('\t'.join(tokens) +'\n')
                finally:
                    if search_conn: search_conn.close()
           
            p_id_prev = None
            projected_size = 0
            curr_size = 0
            tranches_internal = {}
            for line in sort_proc.stdout:
                zinc_id, p_id = line.decode('utf-8').strip().split()
                if p_id != p_id_prev and p_id_prev != None:
                    t_elapsed = time.time() - t_start
                    printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
                    
                    search(p_id_prev, data_file, output_file, tranches_internal, args)
                
                    curr_size += projected_size
                    projected_size = 0
                    tranches_internal.clear()
                    data_file.seek(0)
                    data_file.truncate()
                sub_id, tranche = get_sub_id(zinc_id), get_tranche(zinc_id)
                tranche_id_int = tranches_internal.get(tranche)

                # instead of copying the tranche configuration over from the backend server, we just create our own here
                # we don't use tranche information from zinc22, we keep the tranche information encoded in the input zinc id. 
                # zinc22 tranches have occasionally mutated one or two off and we want to avoid user confusion (what is this new zinc id doing in my output ?!)
                if not tranche_id_int:
                    # the whole point of this is to reduce the overhead of carrying the original tranche information through the query, so reduce it to smallint size (char(2)) instead of char(8)
                    tranche_id_int = len(tranches_internal)+1
                    assert(tranche_id_int < 65536) # keep size under postgres smallint limit
                    tranches_internal[tranche] = tranche_id_int

                data_file.write(str(sub_id) + '\t' + str(tranche_id_int) + '\n')
                projected_size += 1
                p_id_prev = p_id
            if projected_size > 0:
                t_elapsed = time.time() - t_start
                printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)

                search(p_id_prev, data_file, output_file, tranches_internal, args)
                
        t_elapsed = time.time() - t_start
        printProgressBar(total_length, total_length, prefix = "", suffix="done searching sn!", length=50, t_elapsed=t_elapsed)
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="search for smiles by zinc22 id")

    parser.add_argument("input_file", type=str, help="file containing list of zinc ids to look up")
    parser.add_argument("results_out", type=str, help="destination file for output")
    parser.add_argument("--vendor-search", action='store_true', default=False, help="look up molecules by vendor code instead of zinc id")
    parser.add_argument("--get-vendors", action='store_true', default=False, help="get vendor supplier codes associated with zinc id")
    parser.add_argument("--configuration-server-url", type=str, default=SQLALCHEMY_BINDS["zinc22_common"], help="database containing configuration for zinc22 system")
    
    # hard coding this for now
    client_configuration = {
        "mem_max_sort" : int(5.12e8), # in bytes
        #"mem_max_cached_file" : int(2.56e8), # in bytes
        "mem_max_cached_file" : 0
    }

    args = parser.parse_args()
    
    if not args.vendor_search:
        zinc_id_search(args, client_configuration)
    else:
        vendor_search(args, client_configuration)
