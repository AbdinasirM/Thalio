def verify(code:str):
    #check it if it exists in the db
    #TRUE:
        #Check if the time now is greater than the expires:
            #True:
                #dont let the user update password
            #False:
                #let the user update password for their account
    #if it doesn't exist then return error
                