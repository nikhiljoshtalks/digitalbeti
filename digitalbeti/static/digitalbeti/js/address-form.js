$(document).ready(() => {
    $('#id_permanent-state').on('change', (e) => {
            let state_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/districts",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name})
            }).then(data => {
                //Populate the district drop down
                let option = '';
                const stateLen = data.districts.length;
                $('#id_permanent-district').empty();
                $('#id_permanent-subdistrict').empty();
                $('#id_permanent-village').empty();
                for (var i = 0; i < stateLen; i++) {
                    option = '<option value="' + data.districts[i] + '">' + data.districts[i] + '</option>';
                    $('#id_permanent-district').append(option);
                }
                $('#id_permanent-district').trigger('change');
            })
        }
    );
    $('#id_permanent-district').on('change', (e) => {
            state_name = $('#id_permanent-state')[0].value;
            district_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/cities",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name, 'district': district_name})
            }).then(data => {
                //Populate the district drop down
                var option = '';
                var stateLen = data.cities.length;
                $('#id_permanent-subdistrict').empty();
                $('#id_permanent-village').empty();
                for (var i = 0; i < stateLen; i++) {
                    option = '<option value="' + data.cities[i] + '">' + data.cities[i] + '</option>';
                    $('#id_permanent-subdistrict').append(option);
                }
                $('#id_permanent-subdistrict').trigger('change');
            })
        }
    );
    $('#id_permanent-subdistrict').on('change', (e) => {
            state_name = $('#id_permanent-state')[0].value;
            district_name = $('#id_permanent-district')[0].value;
            subdistrict_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/villages",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name, 'district': district_name, 'subdistrict': subdistrict_name})
            }).then(data => {
                //Populate the district drop down
                var option = '';
                var stateLen = data.villages.length;
                $('#id_permanent-village').empty();
                for (var i = 0; i < stateLen; i++) {
                    option = '<option value="' + data.villages[i] + '">' + data.villages[i] + '</option>';
                    $('#id_permanent-village').append(option);
                }
            })
        }
    );
    $('#id_state').on('change', (e) => {
            let state_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/districts",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name})
            }).then(data => {
                //Populate the district drop down
                let option = '';
                const stateLen = data.districts.length;
                $('#id_district').empty();
                $('#id_subdistrict').empty();
                $('#id_village').empty();
                for (var i = 0; i < stateLen; i++) {
                    option = '<option value="' + data.districts[i] + '">' + data.districts[i] + '</option>';
                    $('#id_district').append(option);
                }
                $('#id_district').trigger('change');
            })
        }
    );
    $('#id_district').on('change', (e) => {
            state_name = $('#id_state')[0].value;
            district_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/cities",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name, 'district': district_name})
            }).then(data => {
                //Populate the district drop down
                var option = '';
                var stateLen = data.cities.length;
                $('#id_subdistrict').empty();
                $('#id_village').empty();
                for (var i = 0; i < stateLen; i++) {
                    option = '<option value="' + data.cities[i] + '">' + data.cities[i] + '</option>';
                    $('#id_subdistrict').append(option);
                }
                $('#id_subdistrict').trigger('change');
            })
        }
    );
    $('#id_subdistrict').on('change', (e) => {
            state_name = $('#id_state')[0].value;
            district_name = $('#id_district')[0].value;
            subdistrict_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/villages",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name, 'district': district_name, 'subdistrict': subdistrict_name})
            }).then(data => {
                //Populate the district drop down
                var option = '';
                var stateLen = data.villages.length;
                $('#id_village').empty();
                for (var i = 0; i < stateLen; i++) {
                    option = '<option value="' + data.villages[i] + '">' + data.villages[i] + '</option>';
                    $('#id_village').append(option);
                }
            })
        }
    );

    $('#id_permanent-state').trigger('change');
    $('#id_state').trigger('change');
});
