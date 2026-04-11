import pytest
from envdiff.templater import EnvTemplater, TemplateKey, TemplateResult


@pytest.fixture
def templater():
    return EnvTemplater()


@pytest.fixture
def sample_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "PORT": "8080",
        "APP_NAME": "myapp",
    }


def test_generate_returns_template_result(templater, sample_env):
    result = templater.generate(sample_env, source_name="test.env")
    assert isinstance(result, TemplateResult)
    assert result.source_name == "test.env"


def test_generate_total_keys(templater, sample_env):
    result = templater.generate(sample_env)
    assert result.total_keys == len(sample_env)


def test_sensitive_key_gets_secret_placeholder(templater):
    env = {"API_KEY": "real-secret-value"}
    result = templater.generate(env)
    assert result.keys[0].placeholder == "<secret>"


def test_password_key_gets_secret_placeholder(templater):
    env = {"DB_PASSWORD": "hunter2"}
    result = templater.generate(env)
    assert result.keys[0].placeholder == "<secret>"


def test_numeric_value_gets_number_placeholder(templater):
    env = {"TIMEOUT": "30"}
    result = templater.generate(env)
    assert result.keys[0].placeholder == "<number>"


def test_bool_value_gets_bool_placeholder(templater):
    env = {"ENABLE_FEATURE": "true"}
    result = templater.generate(env)
    assert result.keys[0].placeholder == "<bool>"


def test_debug_key_is_optional(templater):
    env = {"DEBUG": "false"}
    result = templater.generate(env)
    assert result.keys[0].required is False


def test_app_name_is_required(templater):
    env = {"APP_NAME": "myapp"}
    result = templater.generate(env)
    assert result.keys[0].required is True


def test_required_keys_filter(templater, sample_env):
    result = templater.generate(sample_env)
    for k in result.required_keys:
        assert k.required is True


def test_optional_keys_filter(templater, sample_env):
    result = templater.generate(sample_env)
    for k in result.optional_keys:
        assert k.required is False


def test_render_contains_source_name(templater, sample_env):
    result = templater.generate(sample_env, source_name="staging.env")
    rendered = result.render()
    assert "staging.env" in rendered


def test_render_contains_all_keys(templater, sample_env):
    result = templater.generate(sample_env)
    rendered = result.render()
    for key in sample_env:
        assert key in rendered


def test_template_key_render_includes_required_marker():
    tk = TemplateKey(key="FOO", placeholder="CHANGE_ME", required=True)
    assert "REQUIRED" in tk.render()


def test_template_key_render_includes_optional_marker():
    tk = TemplateKey(key="FOO", placeholder="CHANGE_ME", required=False)
    assert "OPTIONAL" in tk.render()


def test_generate_merged_covers_all_keys(templater):
    envs = {
        "dev": {"FOO": "1", "BAR": "2"},
        "prod": {"FOO": "1", "BAZ": "3"},
    }
    result = templater.generate_merged(envs)
    keys = {k.key for k in result.keys}
    assert keys == {"FOO", "BAR", "BAZ"}
    assert result.source_name == "merged"
