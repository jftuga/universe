#!/bin/sh

# last checked Nov-14-2011

# APNIC
# http://www.apnic.net/publications/research-and-insights/ip-address-trends/apnic-resource-range

# http://www.completewhois.com/statistics/data/ips-bycountry/rirstats/
# is another possible source of country IP network information

# http://iplocationtools.com/ip_country_block.php
# is another possible source of country IP network information

# http://www.okean.com/thegoods.html
# specifically focuses on Chinese and Korean IP block assignments

# See also:
# http://en.wikipedia.org/wiki/List_of_Internet_top-level_domains
# http://www.iana.org/assignments/ipv4-address-space/
# https://www.countryipblocks.net/

# ae=united_arab_emirates
# af=afghanistan
# al=albania
# ar=argentina
# az=azerbaijan
# be=belgium
# bg=bulgaria
# bj=benin
# bo=bolivia
# br=brazil
# by=belarus
# cc=cocos_islands
# ci=côte_dIvoire
# cl=chile
# cn=china
# co=columbia
# cr=costa_rica
# cs=serbia 
# cu=cuba
# cz=czech_republic
# do=dominican_republic
# dz=algeria
# ec=ecuador
# ee=estonia
# eg=egypt
# ge=georgia
# gr=greece
# gs=south_georgia_islands
# hk=hong_kong
# hr=croatia
# hu=hungary
# id=indonesia
# il=israel
# in=india
# iq=iraq
# ir=iran
# it=italy
# kp=north_korea
# kr=south_korea
# kz=Kazakstan
# lb=lebanon
# lt=lithuania
# lv=latvia
# kw=kuwait
# ma=morocco
# md=moldova
# mk=macedonia
# my=malaysia
# ng=nigeria
# nl=netherlands
# nu=niue
# pe=peru
# ph=philippines
# pl=poland
# py=paraguay
# qa=qatar
# ro=romania
# ru=russia
# rs=serbia
# sa=saudia_arabia
# sg=singapore
# sk=slovakia
# sn=senegal
# st=sao_tome
# sv=slovakia
# tc=turks_caicos
# th=thailand
# tk=tokelau
# to=tonga
# tr=turkey
# tt=trinidad_tobago
# tw=taiwan
# tv=tuvalu
# ua=ukraine
# uy=uruguay
# uz=uzbekistan
# ve=venezuela
# vn=vietnam
# ws=samoa
# yu=yugoslavia 
# za=south_africa

COUNTRIES="ae af al ar az be bg bj bo br by cc ci cl cn co cr cs cu cy cz do dz ec ee eg ge gr gs hk hr hu id il in iq ir it kp kr kz lb lt lv kw ma md mk my ng nl nu pe ph pl py qa ro ru rs sa sg sk sn st sv tc th tk to tr tt tw tv ua uy uz ve vn ws yu za"
#AGENT="'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'"

Download() {
	C=$1
	#rm -f ${C}.txt
	if [ ! -e countries/${C}.txt ] ; then
		URL="http://ip.ludost.net/cgi/process?country=1&country_list=${C}&format_template=prefix&format_name=&format_target=&format_default="
		echo downloading ${C}
		wget --quiet -O countries/${C}.txt ${URL}
		sleep .4
	fi
	echo
	ls -l countries/${C}.txt
	echo
}

for C in $COUNTRIES ; do
	echo $C
	Download $C
done


