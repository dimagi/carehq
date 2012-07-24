echo "***** Removing local carehq_prod database *****"
curl -X DELETE http://admin:dimagi4vm@192.168.56.101:5984/ashand_study3/

echo "***** Creating carehq_prod database *****"
curl -X PUT http://admin:dimagi4vm@192.168.56.101:5984/ashand_study3/

python manage.py syncdb
python manage.py reset_tenants
python manage.py ashand_init
python manage.py runscript generate_careteams
#python manage.py runscript random_inject

