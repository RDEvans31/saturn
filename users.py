users = {
    'rob': {
        'weekly': True,
        'daily_buy_amount': 2,
        'exchanges': {
            'ftx': {
                'symbols':['ETH/USD', 'SOL/USD', 'MATIC/USD'],
                'api':{
                    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
                    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
                    'enableRateLimit': True,
                },
                'header': {'FTX-SUBACCOUNT':'Savings'}
            },
            'cex':{
                'symbols':['ADA/USD'],
                'api':{
                    'uid' : 'up109520414',
                    'apiKey': '1X2uEcPlvBCe4CcMtzWKguG1SDI',
                    'secret': '8JY4fDg6hRz0DTolZHz77XPdC1o',
                    'enableRateLimit': True,
                }
            }
        }
    },
    'edward': {
        'weekly': True, 
        'daily_buy_amount':1,
        'exchanges': {
            'ftx': {
                'symbols':['BTC/USD', 'ETH/USD'],
                'api':{
                    'apiKey': 'urrL3uM7B8yRZwq54WQXUgxX21NyI6AxQ0xv1lC7',
                    'secret': 'vE9rU4lcNRE-CQmA9IAOX4K1r0Jlr5kskUpEc7BK',
                    'enableRateLimit': True,
                }
            }
        }
    }
}