<div x-show="vote" x-transition>
    <template x-if="!submitted">
        <form class="mt-3" @submit.prevent="submitFeedback">
            <div class="field">
                <label class="label">Optional comment:</label>
                <div class="control">
                    <textarea class="textarea" x-model="comment" placeholder="Your feedback..."></textarea>
                </div>
            </div>
            <div class="is-grouped field">
                <div class="control">
                    <button class="button is-link" type="submit" x-bind:disabled="submitting">
                        <span x-show="submitting">Submitting…</span>
                        <span x-show="!submitting">Submit Feedback</span>
                    </button>
                </div>
            </div>
        </form>
    </template>

    <template x-if="submitted">
        <div class="mt-3 notification is-success">
            ✅ Thank you for your feedback!
        </div>
    </template>
</div>
