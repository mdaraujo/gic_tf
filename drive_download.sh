code=`wget --save-cookies cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=0B2JbaJSrWLpza08yS2FSUnV2dlE' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p'`
wget --load-cookies cookies.txt -O YOLO_small.ckpt 'https://drive.google.com/uc?export=download&confirm='$code'&id=0B2JbaJSrWLpza08yS2FSUnV2dlE'

rm cookies.txt
