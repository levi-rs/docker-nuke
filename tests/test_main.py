import mock

from docker.models.containers import Container
from docker.models.images import Image
from docker.models.volumes import Volume
import pytest

from dockernuke import nuke


CNTR_NAME = "mock container name"
IMG_TAGS = ["mock image tag", ]
IMG_ID = 'mock image id'
VOL_NAME = "mock volume name"


@pytest.fixture()
def cntr():
    """ Docker container fixture """
    container = mock.create_autospec(Container)
    container.name = CNTR_NAME
    return container


@pytest.fixture()
def img():
    """ Docker image fixture """
    image = mock.create_autospec(Image)
    image.tags = IMG_TAGS
    return image


@pytest.fixture()
def vol():
    """ Docker volume fixture """
    volume = mock.create_autospec(Volume)
    volume.name = VOL_NAME
    return volume


@pytest.fixture()
def client(cntr, img, vol):
    """ Docker client fixture """
    with mock.patch('dockernuke.main.docker') as docker:
        docker.from_env.return_value = docker
        docker.containers.list.return_value = [cntr, ]
        docker.images.list.return_value = [img, ]
        docker.volumes.list.return_value = [vol, ]
        yield docker


def test_nothing_to_remove(client):
    """ Verify nothing happens if the docker client returns no objects """
    client.containers.list.return_value = list()
    client.images.list.return_value = list()
    client.volumes.list.return_value = list()

    nuke()

    # Check Client calls
    assert client.from_env.called
    assert client.containers.list.called
    assert client.images.list.called
    assert not client.images.remove.called
    assert client.volumes.list.called


def test_everything_removed(client):
    """ Verify all objects are stopped/removed """
    nuke()

    # Check Client calls
    assert client.from_env.called
    assert client.containers.list.called
    assert client.images.list.called
    assert client.images.remove.called
    assert client.volumes.list.called

    # Check Container calls
    assert client.containers.list()[0].stop.called
    assert client.containers.list()[0].remove.called

    # Check Image calls
    assert client.images.remove.called
    assert mock.call(client.images.list()[0].id) == client.images.remove.call_args

    # Check Volume calls
    assert client.volumes.list()[0].remove.called
