function onMouseOverNavbarDropdownItem(item) {
    for(let child of item.children) {
        child.classList.add("show");
    }
}

function onMouseLeaveNavbarDropdownItem(item) {
    for(let child of item.children) {
        child.classList.remove("show");
    }
}
function onSortByFieldClickListener(orderName, fieldName) {
    const urlParams = new URLSearchParams(window.location.search);
    if(urlParams.get(orderName) == fieldName) {
        urlParams.set(orderName, `-${fieldName}`);
    } else {
        urlParams.set(orderName, fieldName);
    }
    window.location.search = urlParams;
    return urlParams.get(orderName);
}

function onSortNetsByFieldClickListener(fieldName) {
    onSortByFieldClickListener("order-nets-by", fieldName);
}

function onSortResultsByFieldClickListener(fieldName) {
    onSortByFieldClickListener("order-results-by", fieldName);
}

function onSortVideosByFieldClickListener(fieldName) {
    onSortByFieldClickListener("order-videos-by", fieldName);
}

function onSortDatasetsByFieldClickListener(fieldName) {
    onSortByFieldClickListener("order-datasets-by", fieldName);
}

function onSortNetworksByNameClickListener() {
    onSortNetsByFieldClickListener('name');
}

function onSortNetworksByTypeClickListener() {
    onSortNetsByFieldClickListener('neural_network_type');
}

function onSortNetworksByTestFractionClickListener() {
    onSortNetsByFieldClickListener('test_fraction')
}

function onSortNetworksByNumEpochsClickListener() {
    onSortNetsByFieldClickListener('num_epochs');
}

function onSortNetworksByStartedTrainingAtClickListener() {
    onSortNetsByFieldClickListener('started_training_at');
}

function onSortNetworksByFinishedTrainingAtClickListener() {
    onSortNetsByFieldClickListener('finished_training_at');
}

function onSortAnalysisByStartedInferenceAtClickListener() {
    onSortResultsByFieldClickListener('started_inference_at');
}

function onSortAnalysisByFinishedInferenceAtClickListener() {
    onSortResultsByFieldClickListener('finished_inference_at');
}