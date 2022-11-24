import pytest

from userservices import UserService

class TestUserService:

    #Must have 12 characters - Test should fail.
    def test_complex_password_one(sefl):
        assert UserService.check_password_complexity('aBZ32#$cd') is False

    #Must have 2 upper case characters - Test should fail.
    def test_complex_password_two(sefl):
        assert UserService.check_password_complexity('abkdircd#@987') is False
    
    #Must have 2 Numeric characters - Test should fail.
    def test_complex_password_three(sefl):
        assert UserService.check_password_complexity('labdjfWIe9cd#@KL') is False
    
    #Must have 2 Special characters - Test should fail.
    def test_complex_password_four(sefl):
        assert UserService.check_password_complexity('labdjfWIe92cdKL') is False

    #Must have password complexity score above 66% - Test should fail.
    def test_complex_password_five(sefl):
        assert UserService.check_password_complexity('aaaaaaa#@KS12') is False
    
    #Must have 12 characters in total, 2 special characters, 2 Numberic characters, 2 uppercase characters and a 
    def test_complex_password_six(sefl):
        assert UserService.check_password_complexity('lkdfjlkdfjdfjkdlskjflkdjflkdjflkff#@KS12')

    
    
    
    