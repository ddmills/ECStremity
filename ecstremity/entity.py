from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING, Union

from collections import  defaultdict

from ecstremity import Component
from .entity_event import EntityEvent

if TYPE_CHECKING:
    from ecstremity import Engine


class Entity(defaultdict):
    """A big ol' bag of Components!

    The Entity class extends the `defaultdict` from the `collections` package.
    To access a component on this entity, simply index the entity directly,
    using either the class symbol for the component or the component's string
    accessor name. The following are all valid:

        position = Entity[Position]\n
        position = Entity["Position"]\n
        position = Entity["POSITION"]\n
        position = Entity["pOsITiOn"]
    """

    def __init__(self, ecs: Engine, uid: Optional[str] = None) -> None:
        """Constructor.

        - ecs: Engine           the ecstremity Engine instance
        - uid: str              unique ID generated by the Engine.
        """
        self.ecs = ecs
        self.uid = uid if uid is not None else self.ecs.generate_uid()
        self._is_destroyed: bool = False

    @property
    def is_destroyed(self) -> bool:
        """Returns True if this entity has been destroyed."""
        return self._is_destroyed

    @property
    def components(self):
        """Return an iterable of all component instances attached to entity."""
        return self.items()

    def add(self, component: Union[str, Component], properties: Dict[str, Any]) -> bool:
        """Create and add a registered component to the entity initialized with
        the specified properties.

        A component instance can be supplied instead.
        """
        component = self.ecs.create_component(component, properties)
        return self._attach(component)

    def destroy(self):
        """Destroy this entity and all attached components."""
        self._is_destroyed = True
        for component in self.values():
            component.destroy()
        self.ecs.entities.on_entity_destroyed(self)

    def fire_event(self, name: str, data: Optional[Any] = None):
        evt = EntityEvent(name, data)
        for component in self.values():
            if isinstance(component, Component):
                component._on_event(evt)
                if evt.prevented:
                    return evt

            # TODO Logic for nested components.

        return evt

    def has(self, component: Union[str, Component]):
        """Check if a component is currently attached to this Entity."""
        try:
            if isinstance(component, str):
                components = self[component]
            else:
                components = self[component.name]
            if components:
                return True
        except KeyError:
            return False

    def owns(self, component: Component) -> bool:
        """Check if target component has this entity as an owner."""
        return component.entity == self

    def remove(self, component: Union[str, Component]) -> Optional[Component]:
        """Remove a component from the entity."""
        if isinstance(component, str):
            return self[component].remove()
        return self[component].remove()

    def serialize(self):
        """TODO"""
        pass

    def _attach(self, component: Component) -> bool:
        self[component.name] = component
        component._on_attached(self)
        return True

    def __getitem__(self, component: Union[str, Component]) -> Component:
        if not isinstance(component, str):
            component = component.name
        return super().__getitem__(component.upper())

