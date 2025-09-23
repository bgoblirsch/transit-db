#################
## Route Tests ##
#################
cli route-list
cli route-add 99 "Silver Line" -t rail
cli route-update 99 --name "Pritzker Line"
cli route-get "Pritzker Line"
cli route-delete 99

#######################
## Maintenance Tests ##
#######################
cli maintenance-list --vehicle 11

# Error test: Vehicle 30 does not exist.
cli maintenance-add 30 2025-05-10 "Brake inspection" 

cli maintenance-add 10 2025-05-10 "Brake inspection"
cli maintenance-list 
cli maintenance-update 38 --work-performed "Brake inspection and tire replacement"
cli maintenance-delete 38

##################
## Driver Tests ##
##################
cli driver-add "Larry David" -c "Bus Only" -s "2020-05-01" -p 45
cli driver-list    
cli driver-update 21 -c "Bus and Metro" -p 48.50
cli driver-delete 21

################
## Trip Tests ##
################

# Database Error: Driver is already assigned to a different route that day.
cli trip-add 99 2 1 9 2025-01-01 N 