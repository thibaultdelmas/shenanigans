import ssl

context = ssl.create_default_context()
der_certs = context.get_ca_certs(binary_form=True)
pem_certs = [ssl.DER_cert_to_PEM_cert(der) for der in der_certs]

with open('wincacerts.pem', 'w') as outfile:
    for pem in pem_certs:
        outfile.write(pem + '\n')

