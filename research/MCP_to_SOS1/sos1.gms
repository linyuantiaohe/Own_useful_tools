kkt_newng(R,NG)..    NGPAR('FC',NG)*DR1+NGPAR('OMC',NG)*DR2-sum((M,H),a_ngoutput(M,H,R,NG)*NGPAR('UP',NG))-sum((M,H),(a_ngrampup(M,H,R,NG)+a_ngrampdown(M,H,R,NG))*RAMP(H,NG))=e=0;
kkt_newrg(R,RG)..    RGFC(R,RG)*DR1+RGOMC(R,RG)*DR2-sum((M,H),a_rgoutput(M,H,R,RG)*RGCFUP(M,H,R,RG))=e=0;
kkt_ngpp(M,H,R,NG).. NGVC(R,NG)*DAYS(M)*3*DR2-NGFIT(R,NG)*DR2-a_demandmeet(M,H,R)+a_ngoutput(M,H,R,NG)-a_ngrampup(M,H,R,NG)+a_ngrampup(M,H-1,R,NG)+a_ngrampdown(M,H,R,NG)-a_ngrampup(M,H-1,R,NG)=e=0;
kkt_rgpp(M,H,R,RG).. -RGFIT(R,RG)*DR2-a_demandmeet(M,H,R)+a_rgoutput(M,H,R,RG)-a_recmeet(R)*DAYS(M)*3=e=0;
kkt_ppf(M,H,R,R1)..  (powpri(M,H,R1,R)+TVC(R1,R))*DAYS(M)*3*DR2-a_demandmeet(M,H,R)*TEF(R1,R)=e=0;
kkt_pst(M,H,R,R1)..  -powpri(M,H,R,R1)*DAYS(M)*3*DR2+a_demandmeet(M,H,R)=e=0;
kkt_recst(R,R1)..    -recpri(R,R1)*DR2+a_recmeet(R)=e=0;
kkt_recpf(R,R1)..    recpri(R1,R)*DR2-a_recmeet(R)=e=0;
