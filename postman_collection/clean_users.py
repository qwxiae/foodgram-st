from django.contrib.auth import get_user_model

User = get_user_model()

usernames_list = [
    "vasya.ivanov",
    "second-user",
    "third-user-username",
    "NoEmail",
    "NoFirstName",
    "NoLastName",
    "NoPassword",
    "TooLongEmail",
    "the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-",
    "TooLongFirstName",
    "TooLongLastName",
    "InvalidU$ername",
    "EmailInUse",
]

emails_list = [
    "vasya@example.com",
    "second@example.com",
    "third@example.com",
    "noemail@example.com",
    "duplicate@example.com",
]

qs1 = User.objects.filter(username__in=usernames_list)
qs2 = User.objects.filter(email__in=emails_list)

deleted_1, _ = qs1.delete()
deleted_2, _ = qs2.delete()

total_deleted = deleted_1 + deleted_2

print("Users deleted:", total_deleted)
