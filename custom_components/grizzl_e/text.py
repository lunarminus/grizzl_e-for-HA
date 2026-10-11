"""Name field for adding a schedule from the dashboard (cloud entries)."""
from homeassistant.components.text import TextEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity

from .cloud import GrizzleECloudEntity, is_cloud_entry
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    if not is_cloud_entry(entry) or entry.entry_id not in hass.data.get(DOMAIN, {}):
        return
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([GrizzleENewScheduleName(coordinator)])


class GrizzleENewScheduleName(GrizzleECloudEntity, RestoreEntity, TextEntity):
    """Name of the schedule the Add Schedule button creates."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:calendar-edit"
    _attr_native_min = 1
    _attr_native_max = 64

    def __init__(self, coordinator):
        super().__init__(coordinator, "new_schedule_name", "New Schedule Name")

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in ("unknown", "unavailable", ""):
            self.coordinator.schedule_draft.name = last_state.state[: self._attr_native_max]

    @property
    def native_value(self):
        return self.coordinator.schedule_draft.name

    async def async_set_value(self, value):
        self.coordinator.schedule_draft.name = value
        self.async_write_ha_state()
