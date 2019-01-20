import manager

test = manager.project('test_project')

print(test)

print(test.calculations[2].com.content)

test.calculations[2].com.description =['AAAAAAAASCCHEDUREEEEEEEO']
test.calculations[2].com.write_content()
print(test.calculations[2].com.content)
