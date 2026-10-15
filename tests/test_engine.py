import pytest
from backend.engine import parse_repo,explain
@pytest.mark.parametrize('x,y',[('owner/repo','owner/repo'),('https://github.com/owner/repo','owner/repo'),('https://github.com/owner/repo/issues','owner/repo')])
def test_parse(x,y):assert parse_repo(x)==y
@pytest.mark.parametrize('x',['https://evil.com/a/b','bad','https://github.com/a'])
def test_bad(x):
 with pytest.raises(ValueError):parse_repo(x)
def test_security_disclaimer():
 assert 'not verified' in explain({'repo':'x/y','evidence':[],'verdict':'unknown'},'is this code safe?')

@pytest.mark.parametrize('value', [
    'http://github.com/owner/repo',
    'https://github.com.evil.com/owner/repo',
    'https://user:password@github.com/owner/repo',
    'https://github.com:8443/owner/repo',
    'https://github.com/owner/repo?tab=readme',
    'https://github.com/owner/repo#readme',
    'https://github.com/owner//repo',
    'owner/..',
    '../repo',
])
def test_reject_ambiguous_repository_inputs(value):
    with pytest.raises(ValueError):
        parse_repo(value)

def test_git_suffix():
    assert parse_repo('https://github.com/owner/repo.git') == 'owner/repo'
