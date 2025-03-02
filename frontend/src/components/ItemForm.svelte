<script lang="ts">
    import { addAlert } from "$lib/alert";
    import { itemForm, categories } from "$lib/store";
    import { possibleUnits } from "$lib/types";
    import { Button, Modal, Label, Input } from "flowbite-svelte";
    import CategoryForm from "./CategoryForm.svelte";
    import { api } from "$lib/auth";

    async function submitItem() {
        if ($itemForm.mode == "edit") {
            api.itemUpdate($itemForm.itemID, $itemForm.item)
                .then((_) => {
                    $itemForm.isOpen = false;
                    $itemForm.itemID = -1;
                })
                .catch((res) => {
                    addAlert(
                        `Failed to update the item '${$itemForm.item.name}':${res.error}`,
                        "error",
                    );
                });
            return;
        } else if ($itemForm.mode == "add") {
            if (!$itemForm.item.name) {
                addAlert("Name is required", "error");
                return;
            }
            if (!$itemForm.item.category_id) {
                addAlert("Category is required", "error");
                return;
            }
            if (!$itemForm.item.unit) {
                $itemForm.item.unit = "None";
            }
            if (!$itemForm.item.notes) {
                $itemForm.item.notes = "";
            }
            api.itemCreate({
                name: $itemForm.item.name,
                notes: $itemForm.item.notes,
                quantity: $itemForm.item.quantity,
                unit: $itemForm.item.unit,
                category_id: $itemForm.item.category_id,
            })
                .then((_) => {
                    $itemForm.isOpen = false;
                })
                .catch((res) => {
                    addAlert(
                        `Failed to create the item '${$itemForm.item.name}':${res.error}`,
                        "error",
                    );
                });
        }
    }

    async function deleteItem() {
        api.itemDelete($itemForm.itemID)
            .then((_) => {
                $itemForm.isOpen = false;
                $itemForm.itemID = -1;
            })
            .catch((res) => {
                addAlert(
                    `Failed to delete the item '${$itemForm.item.name}':${res.error}`,
                    "error",
                );
            });
    }
</script>

<Modal
    bind:open={$itemForm.isOpen}
    size="xs"
    outsideclose
    class="bg-primaryBg text-primaryText rounded-lg"
>
    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <div
        class="flex flex-col space-y-4 p-1 pt-0 rounded-lg shadow-lg bg-primaryBg text-primaryText"
        role="dialog"
        on:click={(e) => e.stopPropagation()}
        on:keydown={(e) => e.key === "Escape" && ($itemForm.isOpen = false)}
    >
        <Label class="space-y-1 text-sm text-primaryText">
            <span>Name</span>
            <Input
                type="text"
                name="name"
                bind:value={$itemForm.item.name}
                class="bg-secondaryBg border-inputBorderColor rounded-md text-primaryText"
                placeholder="Enter a name"
                required
            />
        </Label>

        <Label class="space-y-1 text-sm text-primaryText">
            <span>Quantity</span>
            <div class="flex items-center space-x-2">
                <Button
                    on:click={() =>
                        ($itemForm.item.quantity = Math.max(
                            0,
                            ($itemForm.item.quantity ?? 0) - 1,
                        ))}
                    class="px-3 py-1 bg-red-500 text-gray-700 rounded-md w-14 h-10 text-3xl"
                >
                    -
                </Button>
                <Input
                    name="quantity"
                    bind:value={$itemForm.item.quantity}
                    class="w-fill text-center bg-secondaryBg border-inputBorderColor rounded-md text-primaryText
                    "
                    placeholder="Enter quantity"
                />
                <Button
                    on:click={() =>
                        ($itemForm.item.quantity =
                            ($itemForm.item.quantity ?? 0) + 1)}
                    class="px-3 py-1 bg-red-500 text-gray-700 rounded-md w-14 h-10 text-xl"
                >
                    +
                </Button>
            </div>
        </Label>

        <div>
            <span class="block text-sm font-medium text-primaryText">Unit</span>
            <div class="m-1 grid grid-cols-4 gap-1">
                {#each possibleUnits as choice}
                    <label
                        class={`inline-flex items-center justify-center p-1 cursor-pointer rounded-md
                         text-primaryText ${choice == $itemForm.item.unit ? "bg-buttonBg" : "bg-secondaryBg"}`}
                    >
                        <input
                            type="radio"
                            value={choice}
                            on:click={() => ($itemForm.item.unit = choice)}
                            name="unit"
                            class="hidden"
                        />
                        {choice}
                    </label>
                {/each}
            </div>
        </div>

        <div>
            <span class="block text-sm font-medium text-primaryText"
                >Category</span
            >
            <div class="m-1 grid grid-cols-3 gap-1">
                {#each $categories as category}
                    <label
                        class={`inline-flex items-center justify-center p-1 cursor-pointer rounded-md
                        text-primaryText max-w-[120px] truncate ${
                            category.id == $itemForm.item.category_id
                                ? "bg-buttonBg"
                                : "bg-secondaryBg"
                        }`}
                        title={category.name}
                    >
                        <input
                            type="radio"
                            value={category}
                            on:click={() =>
                                ($itemForm.item.category_id = category.id)}
                            name="category"
                            class="hidden"
                        />
                        <span class="truncate w-full text-center"
                            >{category.name}</span
                        >
                    </label>
                {/each}

                <label
                    class="inline-flex items-center justify-center p-1 cursor-pointer rounded-md bg-secondaryBg
                        text-primaryText"
                >
                    <CategoryForm />
                </label>
            </div>
        </div>

        <Label class="space-y-1 text-sm text-primaryText">
            <span>Notes</span>
            <Input
                type="text"
                name="notes"
                bind:value={$itemForm.item.notes}
                class="bg-secondaryBg border-inputBorderColor rounded-md text-primaryText"
                placeholder="Enter notes"
            />
        </Label>

        <Button
            type="submit"
            class="w-full py-2 bg-buttonBg text-primaryText font-semibold rounded-md"
            on:click={submitItem}
        >
            {#if $itemForm.mode == "edit"}
                Save
            {:else}
                Add Item
            {/if}
        </Button>

        {#if $itemForm.mode == "edit"}
            <Button
                type="button"
                class="w-full py-2 bg-red-600 hover:bg-red-700 text-primaryText font-semibold rounded-md"
                on:click={deleteItem}
            >
                Delete
            </Button>
        {/if}
    </div>
</Modal>
