"""Start and end times for adding a schedule from the dashboard (cloud entries)."""
from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity

from .cloud import GrizzleECloudEntity, is_cloud_entry
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    if not is_cloud_entry(entry) or entry.entry_id not in hass.data.get(DOMAIN, {}):
        return
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            GrizzleENewScheduleTime(coordinator, "start", "New Schedule Start"),
            GrizzleENewScheduleTime(coordinator, "end", "New Schedule End"),
        ]
    )


class GrizzleENewScheduleTime(GrizzleECloudEntity, RestoreEntity, TimeEntity):
    """Start or end of the schedule the Add Schedule button creates, in the charger's timezone."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator, field, name):
        super().__init__(coordinator, f"new_schedule_{field}", name)
        self._field = field

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is None:
            return
        try:
            restored = time.fromisoformat(last_state.state)
        except ValueError:
            return  # unknown / unavailable
        setattr(self.coordinator.schedule_draft, self._field, restored.replace(second=0, microsecond=0))

    @property
    def native_value(self):
        return getattr(self.coordinator.schedule_draft, self._field)

    async def async_set_value(self, value):
        # The cloud stores hours and minutes only.
        setattr(self.coordinator.schedule_draft, self._field, value.replace(second=0, microsecond=0))
        self.async_write_ha_state()
