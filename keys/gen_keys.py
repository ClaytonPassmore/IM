import rsa

def main():
    (pubkey, privkey) = rsa.newkeys(2048)
    with open('public.pem', 'wb') as fd:
        fd.write(pubkey.save_pkcs1('PEM'))
    with open('private.pem', 'wb') as fd:
        fd.write(privkey.save_pkcs1('PEM'))
    print('Success!')

if __name__ == '__main__':
    main()
