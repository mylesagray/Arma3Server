class Api():
    @staticmethod
    def values():
        return {"key":"value"}

test = Api.values()
print(test)