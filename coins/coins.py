
# 円のコイン(1,5,10,50,100,500)を使って、n 円 を払うパターンの数を計算するプログラム

cache2 = {}
cache3 = {}
cache4 = {}

def coins( n ):
    result = 0

    n2 = n
    while n2>=0:

        result2 = 0

        if cache2.has_key(n2):
            result2 = cache2[n2]
        else:

            n3=n2
            while n3>=0:

                result3 = 0

                if cache3.has_key(n3):
                    result3 = cache3[n3]
                else:

                    n4=n3
                    while n4>=0:

                        result4 = 0

                        if cache4.has_key(n4):
                            result4 = cache4[n4]
                        else:

                            n5=n4
                            while n5>=0:

                                result5 = n5/5 + 1;

                                result4 += result5
                                n5-=10

                            cache4[n4] = result4

                        result3 += result4
                        n4-=50

                    cache3[n3] = result3

                result2 += result3
                n3-=100

            cache2[n2] = result2

        result += result2
        n2-=500

    return result;

def test(n):

    result = coins(n);
    print "%d : %d" % (n, result)

test(10000)

