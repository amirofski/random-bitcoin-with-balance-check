import bit
import random
k = 1
while True:
    pk = bit.Key.from_int(random.randint(1,115792089237316195423570985008687907852837564279074904382605163141518161494337))
    print(pk.address + ' : ' + pk.to_hex() + ' : ' + pk.get_balance('usd'))

    if not pk.get_balance('usd') != 0 :
        print("Matching Key ==== Found!!!\n PrivateKey: " + pk.to_wif())

        f=open(u"winner.txt","a")
        f.write('\nPrivateKey (hex): ' + pk.to_hex())
        f.write('\nPrivateKey (wif): ' + pk.to_wif())
        f.write('\n==================================')
        f.close()
    k += 1
