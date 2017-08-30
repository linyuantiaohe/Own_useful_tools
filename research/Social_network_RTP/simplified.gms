set      t       hour    /1*24/,
         c       controllable appliance  /1*10/,
         i       usertype    /1*3/;

alias (c,cc),(i,ii);

parameter consumer(i);
parameter choosertp(i);

$include D:\code\research\agent based model\demand response\0503\consumernumber


parameter choosefp(i);
choosefp(i)=consumer(i)-choosertp(i);

parameter IRR(t)
/
1        0
2        0
3        0
4        0
5        0
6        0
7        0.016410095
8        0.098328369
9        0.226316315
10       0.341823686
11       0.431397306
12       0.506628788
13       0.536369302
14       0.499615547
15       0.469258558
16       0.378117446
17       0.285012248
18       0.187120942
19       0.081757748
20       0.013022857
21       1.75365E-05
22       0
23       0
24       0
/
;

parameter run(c)
/
1        6
2        7
3        1
4        22
5        5
6        20
7        7
8        14
9        6
10       19
/;

parameter start(i,c),stop(i,c);
start(i,c)=1;
stop(i,c)=24;
start('3',c)$(run(c)-2 gt 1)=run(c)-2;
stop('3',c)$(run(c)+2 lt 24)=run(c)+2;
start('2',c)=run(c);
stop('2',c)=run(c);

parameter ratepower(c)
/
1        0.3
2        0.3
3        0.4
4        1.5
5        0.5
6        1.03
7        1.03
8        1.03
9        0.48
10       1
/;

parameter ul(t)
/
1        0.885
2        0.885
3        0.885
4        0.885
5        0.885
6        0.6
7        0.75
8        0.385
9        0.385
10       1.185
11       1.685
12       1.685
13       1.185
14       1.185
15       1.185
16       0.385
17       0.385
18       0.9
19       1.7
20       1.2
21       1.2
22       1.2
23       0.9
24       0.9
/;

parameter fixdemand(t);
fixdemand(t)=sum(i,ul(t)*consumer(i)+sum(c$(run(c) eq ord(t)),choosefp(i)*ratepower(c)));

scalars  alpha,beta;

alpha=0.35;
beta=0.2;

positive variables CA(i,c,t)     CA load;

CA.up(i,c,t)$((ord(t) ge start(i,c)) and (ord(t) le stop(i,c)))=ratepower(c);
CA.fx(i,c,t)$((ord(t) lt start(i,c)) or (ord(t) gt stop(i,c)))=0;
**************
parameter qag;
qag=sum(i,(sum(t,ul(t))+sum(c,ratepower(c)))*consumer(i))/card(t);
display qag;

equations        catotal(i,c);

catotal(i,c).. sum(t,CA(i,c,t))-ratepower(c)=e=0;

* minimize crtp(i)=sum(t,rtp(t)*(ul(t)+sum(c,CA(i,c,t))))
* rtp(t)=alpha*(fixdemand(t)+sum(i,sum(c,CA(i,c,t))*choosertp(i)))/qag+beta

free variable A1(i,c);

equations       kkt_CA(i,c,t);

kkt_CA(i,c,t).. (alpha/qag*choosertp(i))*(ul(t)+sum(cc,CA(i,cc,t)))+
                                (alpha/qag*(fixdemand(t)+sum(ii,sum(cc,CA(ii,cc,t))*choosertp(ii)))+beta)-A1(i,c)=e=0

model pm /kkt_CA.CA,catotal.A1/;
solve pm using MCP;

parameter rtp(t),costrtp(i),costfp,totalrevenue;
rtp(t)=alpha*(fixdemand(t)+sum(i,sum(c,CA.l(i,c,t))*choosertp(i)))/qag+beta;
costrtp(i)=sum(t,rtp(t)*(ul(t)+sum(c,CA.l(i,c,t))));
costfp=(alpha+beta)*(sum(t,ul(t))+sum(c,ratepower(c)));

totalrevenue=sum(i,costrtp(i)*choosertp(i)+costfp*choosefp(i));

*display rtp,costrtp,costfp,totalrevenue;
file f /D:\code\research\agent based model\demand response\0503\rtpcost/;
put f;
loop(i,put costrtp(i)/);
put costfp/
