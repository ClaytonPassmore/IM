from Crypto.PublicKey import RSA

def main():
    key = RSA.generate(2048)
    pub = key.publickey().exportKey('PEM')
    priv = key.exportKey('PEM')
    with open('public.pem', 'wb') as fd:
        fd.write(pub)
    with open('private.pem', 'wb') as fd:
        fd.write(priv)
    print('Success!')

if __name__ == '__main__':
    main()
